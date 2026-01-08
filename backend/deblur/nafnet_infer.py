import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path


# --- NAFNet architecture (minimal, self contained) ---
class LayerNorm2d(nn.Module):
    """Channel-wise LayerNorm for 2D feature maps."""

    def __init__(self, num_channels: int, eps: float = 1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(num_channels))
        self.bias = nn.Parameter(torch.zeros(num_channels))
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mean = x.mean(1, keepdim=True)
        var = (x - mean).pow(2).mean(1, keepdim=True)
        x = (x - mean) / torch.sqrt(var + self.eps)
        return self.weight[:, None, None] * x + self.bias[:, None, None]


class SimpleGate(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x1, x2 = x.chunk(2, dim=1)
        return x1 * x2


class NAFBlock(nn.Module):
    def __init__(
        self,
        channels: int,
        dw_expand: int = 2,
        ffn_expand: int = 2,
        drop_out_rate: float = 0.0,
    ):
        super().__init__()
        dw_channels = channels * dw_expand
        ffn_channels = channels * ffn_expand

        self.norm1 = LayerNorm2d(channels)
        self.conv1 = nn.Conv2d(channels, dw_channels, kernel_size=1, bias=True)
        self.conv2 = nn.Conv2d(
            dw_channels, dw_channels, kernel_size=3, stride=1, padding=1, groups=dw_channels, bias=True
        )
        self.sca = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(dw_channels // 2, dw_channels // 2, kernel_size=1, bias=True),
        )
        self.conv3 = nn.Conv2d(dw_channels // 2, channels, kernel_size=1, bias=True)
        self.dropout1 = nn.Dropout(drop_out_rate) if drop_out_rate > 0 else nn.Identity()

        self.norm2 = LayerNorm2d(channels)
        self.conv4 = nn.Conv2d(channels, ffn_channels, kernel_size=1, bias=True)
        self.conv5 = nn.Conv2d(ffn_channels // 2, channels, kernel_size=1, bias=True)
        self.dropout2 = nn.Dropout(drop_out_rate) if drop_out_rate > 0 else nn.Identity()

        # Learnable scales
        self.beta = nn.Parameter(torch.zeros((1, channels, 1, 1)), requires_grad=True)
        self.gamma = nn.Parameter(torch.zeros((1, channels, 1, 1)), requires_grad=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x

        x = self.norm1(x)
        x = self.conv1(x)
        x = self.conv2(x)
        x1, x2 = x.chunk(2, dim=1)
        x = x1 * x2
        x = x * self.sca(x)
        x = self.conv3(x)
        x = self.dropout1(x)
        y = residual + x * self.beta

        x = self.norm2(y)
        x = self.conv4(x)
        x1, x2 = x.chunk(2, dim=1)
        x = x1 * x2
        x = self.conv5(x)
        x = self.dropout2(x)

        return y + x * self.gamma


class NAFNet(nn.Module):
    """NAFNet encoder-decoder."""

    def __init__(
        self,
        img_channel: int = 3,
        width: int = 16,
        middle_blk_num: int = 1,
        enc_blk_nums=None,
        dec_blk_nums=None,
        drop_out_rate: float = 0.0,
    ):
        super().__init__()
        if enc_blk_nums is None:
            enc_blk_nums = [1, 1, 1, 1]
        if dec_blk_nums is None:
            dec_blk_nums = [1, 1, 1, 1]

        self.intro = nn.Conv2d(img_channel, width, kernel_size=3, padding=1, bias=True)
        self.ending = nn.Conv2d(width, img_channel, kernel_size=3, padding=1, bias=True)

        self.encoders = nn.ModuleList()
        self.decoders = nn.ModuleList()
        self.downs = nn.ModuleList()
        self.ups = nn.ModuleList()

        channels = width
        for num_blocks in enc_blk_nums:
            self.encoders.append(
                nn.Sequential(*[NAFBlock(channels, drop_out_rate=drop_out_rate) for _ in range(num_blocks)])
            )
            self.downs.append(
                nn.Conv2d(channels, channels * 2, kernel_size=2, stride=2, bias=True)
            )
            channels *= 2

        self.middle_blks = nn.Sequential(
            *[NAFBlock(channels, drop_out_rate=drop_out_rate) for _ in range(middle_blk_num)]
        )

        for num_blocks in dec_blk_nums:
            self.ups.append(
                nn.Sequential(
                    nn.Conv2d(channels, channels * 2, kernel_size=1, bias=False),
                    nn.PixelShuffle(2),
                )
            )
            channels //= 2
            self.decoders.append(
                nn.Sequential(*[NAFBlock(channels, drop_out_rate=drop_out_rate) for _ in range(num_blocks)])
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.intro(x)
        enc_feats = []

        for encoder, down in zip(self.encoders, self.downs):
            x = encoder(x)
            enc_feats.append(x)
            x = down(x)

        x = self.middle_blks(x)

        for decoder, up, enc_feat in zip(self.decoders, self.ups, enc_feats[::-1]):
            x = up(x)
            # Align shapes if padded odd sizes produce off-by-one
            if x.shape[-2:] != enc_feat.shape[-2:]:
                x = F.interpolate(x, size=enc_feat.shape[-2:], mode="bilinear", align_corners=False)
            x = x + enc_feat
            x = decoder(x)

        x = self.ending(x)
        return x


# --- Inference helper ---
class NAFNetDeblur:
    def __init__(self, model_path: str = None, device=None, width: int = 64):
        self.device = torch.device(device) if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = self._resolve_model_path(model_path)
        self.model = self._load_model(self.model_path, width=width)

    def _resolve_model_path(self, model_path):
        if model_path:
            candidate = Path(model_path)
            if candidate.exists():
                return candidate

        # Prefer local deblur folder, then shared weights folder
        candidates = [
            Path(__file__).parent / "nafnet.pth",
            Path(__file__).resolve().parents[1] / "weights" / "NAFNet-GoPro-width64.pth",
        ]
        for cand in candidates:
            if cand.exists():
                return cand

        raise FileNotFoundError(
            "NAFNet weights not found. Expected either deblur/nafnet.pth "
            "or weights/NAFNet-GoPro-width64.pth"
        )

    def _load_model(self, model_path: Path, width: int):
        model = NAFNet(
            img_channel=3,
            width=width,
            middle_blk_num=1,
            enc_blk_nums=[1, 1, 1, 28],
            dec_blk_nums=[1, 1, 1, 1],
        )

        state = torch.load(model_path, map_location=self.device)
        if isinstance(state, dict) and "params" in state:
            state = state["params"]
        model.load_state_dict(state)
        model.to(self.device).eval()

        print(f"[OK] NAFNet loaded: {model_path}")
        print(f"   Device: {self.device}")
        return model

    def _preprocess(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        tensor = torch.from_numpy(img_rgb).permute(2, 0, 1).float().unsqueeze(0) / 255.0
        tensor = tensor.to(self.device)
        # Pad to handle odd sizes (multiple of 16 for 4 downs)
        _, _, h, w = tensor.shape
        mod = 2 ** len(self.model.encoders)
        pad_h = (mod - h % mod) % mod
        pad_w = (mod - w % mod) % mod
        if pad_h or pad_w:
            tensor = F.pad(tensor, (0, pad_w, 0, pad_h), mode="reflect")
        return tensor, pad_h, pad_w

    def _postprocess(self, tensor, pad_h, pad_w):
        if pad_h:
            tensor = tensor[..., : -pad_h, :]
        if pad_w:
            tensor = tensor[..., :, : -pad_w]
        output = tensor.squeeze(0).permute(1, 2, 0).clamp(0, 1).cpu().numpy()
        output = (output * 255.0).round().astype(np.uint8)
        return cv2.cvtColor(output, cv2.COLOR_RGB2BGR)

    def deblur_image(self, img: np.ndarray) -> np.ndarray:
        tensor, pad_h, pad_w = self._preprocess(img)
        with torch.no_grad():
            residual = self.model(tensor)
            output = (tensor + residual).clamp(0.0, 1.0)
        return self._postprocess(output, pad_h, pad_w)


# Global instance to avoid reloading weights for every frame
_nafnet_model = None


def get_deblur_model(model_path: str = None):
    global _nafnet_model
    if _nafnet_model is None:
        _nafnet_model = NAFNetDeblur(model_path)
    return _nafnet_model


def deblur_image(img: np.ndarray, model_path: str = None) -> np.ndarray:
    model = get_deblur_model(model_path)
    return model.deblur_image(img)
