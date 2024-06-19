import re

colours = """Red#FF0000rgb(255, 0, 0) IndianRed#CD5C5Crgb(205, 92, 92) LightCoral#F08080rgb(240, 128, 128) Salmon#FA8072rgb(250, 128, 114) DarkSalmon#E9967Argb(233, 150, 122) LightSalmon#FFA07Argb(255, 160, 122) Crimson#DC143Crgb(220, 20, 60) FireBrick#B22222rgb(178, 34, 34) DarkRed#8B0000rgb(139, 0, 0) """

split_hex = re.findall(r"#[A-Z0-9]{6}", colours)
print(split_hex)