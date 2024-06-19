import re

colours = "Orange#FFA500rgb(255, 165, 0) LightSalmon#FFA07Argb(255, 160, 122) Coral#FF7F50rgb(255, 127, 80) Tomato#FF6347rgb(255, 99, 71) OrangeRed#FF4500rgb(255, 69, 0) DarkOrange#FF8C00rgb(255, 140, 0)"

split_hex = re.findall(r"#[A-Z0-9]{6}", colours)
print(split_hex)