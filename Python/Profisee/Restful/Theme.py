from Profisee.Common import Common, null_guid
from pyparsing import Any

class Theme :
    def __init__(self) :
        pass
        
    @classmethod
    def from_Entity(cls, theme_object:dict[str, Any]) -> Any:
        return cls("").Load(theme_object)

    def to_Theme(self) -> dict[str, Any] :
        return {
            "bannerPrimary": f"{self.BannerPrimary[0]},{self.BannerPrimary[1]},{self.BannerPrimary[2]}",
            "bannerFi": f"{self.BannerFi[0]},{self.BannerFi[1]},{self.BannerFi[2]}",
            "bannerSecondary": f"{self.BannerSecondary[0]},{self.BannerSecondary[1]},{self.BannerSecondary[2]}",
            "contentPrimaryBg": f"{self.ContentPrimaryBg[0]},{self.ContentPrimaryBg[1]},{self.ContentPrimaryBg[2]}",
            "contentPrimaryFi": f"{self.ContentPrimaryFi[0]},{self.ContentPrimaryFi[1]},{self.ContentPrimaryFi[2]}",
            "contentSecondaryBg": f"{self.ContentSecondaryBg[0]},{self.ContentSecondaryBg[1]},{self.ContentSecondaryBg[2]}",
            "contentSecondaryFi": f"{self.ContentSecondaryFi[0]},{self.ContentSecondaryFi[1]},{self.ContentSecondaryFi[2]}",
            "accentBg": f"{self.AccentBg[0]},{self.AccentBg[1]},{self.AccentBg[2]}",
            "accentFi": f"{self.AccentFi[0]},{self.AccentFi[1]},{self.AccentFi[2]}",
            "selectedBg": f"{self.SelectedBg[0]},{self.SelectedBg[1]},{self.SelectedBg[2]}",
            "hyperlink": f"{self.Hyperlink[0]},{self.Hyperlink[1]},{self.Hyperlink[2]}"
        }
        
    def Load(self, theme_object:dict[str, Any]) -> Any:
        self.BannerPrimary = Theme.parse_rgb(Common.Get(theme_object, "bannerPrimary", "255,255,255"))
        self.BannerFi = Theme.parse_rgb(Common.Get(theme_object, "bannerFi", "27, 49, 65"))
        self.BannerSecondary = Theme.parse_rgb(Common.Get(theme_object, "bannerSecondary", "0, 250, 221"))
        self.ContentPrimaryBg = Theme.parse_rgb(Common.Get(theme_object, "contentPrimaryBg", "255, 255, 255"))
        self.ContentPrimaryFi = Theme.parse_rgb(Common.Get(theme_object, "contentPrimaryFi", "107, 114, 128"))
        self.ContentSecondaryBg = Theme.parse_rgb(Common.Get(theme_object, "contentSecondaryBg", "242, 244, 245"))
        self.ContentSecondaryFi = Theme.parse_rgb(Common.Get(theme_object, "contentSecondaryFi", "27, 49, 65"))
        self.AccentBg = Theme.parse_rgb(Common.Get(theme_object, "accentBg", "19, 97, 134"))
        self.AccentFi = Theme.parse_rgb(Common.Get(theme_object, "accentFi", "255, 255, 255"))
        self.SelectedBg = Theme.parse_rgb(Common.Get(theme_object, "selectedBg", "211, 237, 249"))
        self.Hyperlink = Theme.parse_rgb(Common.Get(theme_object, "hyperlink", "19, 98, 134"))
        return self
    
    @staticmethod
    def parse_rgb(value: str) -> tuple[int, int, int]:
        parts = value.split(',')
        
        if len(parts) != 3:
            raise ValueError("Input must contain exactly three comma-separated values.")
        
        try:
            r, g, b = (int(part.strip()) for part in parts)
        except ValueError as e:
            raise ValueError("All parts must be integers.") from e

        for color in (r, g, b):
            if not (0 <= color <= 255):
                raise ValueError("Color values must be between 0 and 255.")
        return r, g, b
    
"""
{
  "bannerPrimary": "255,255,255",
  "bannerFi": "27, 49, 65",
  "bannerSecondary": "0, 250, 221",
  "contentPrimaryBg": "255, 255, 255",
  "contentPrimaryFi": "107, 114, 128",
  "contentSecondaryBg": "242, 244, 245",
  "contentSecondaryFi": "27, 49, 65",
  "accentBg": "19, 97, 134",
  "accentFi": "255, 255, 255",
  "selectedBg": "211, 237, 249",
  "hyperlink": "19, 98, 134"
}
"""