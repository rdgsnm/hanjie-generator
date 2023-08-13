from typing import Tuple
from PIL import Image, ImageDraw, ImageFont

from hanjie_base import HanjieBase


class HanjieImageBuilder:
    def __init__(self, hanjie: HanjieBase):
        self.hanjie = hanjie

    def draw_clues(
        self,
        draw: ImageDraw.Draw,
        cell_size: int,
        font: ImageFont.FreeTypeFont,
        offset_x: int,
        offset_y: int,
    ) -> Tuple[int, int]:
        max_row_clue_len: int = max(len(clue) for clue in self.hanjie.row_clues)
        max_col_clue_len: int = max(len(clue) for clue in self.hanjie.col_clues)

        for i, clue in enumerate(self.hanjie.row_clues):
            for j, number in enumerate(clue):
                x_position: int = (
                    (max_row_clue_len - len(clue) + j) * cell_size
                    + offset_x
                    - cell_size
                )
                y_position: int = i * cell_size + offset_y

                draw.text(
                    (x_position, y_position), str(number), font=font, fill=(0, 0, 0)
                )

        for i, clue in enumerate(self.hanjie.col_clues):
            for j, number in enumerate(clue):
                x_position: int = i * cell_size + offset_x
                y_position: int = (
                    (max_col_clue_len - len(clue) + j) * cell_size
                    + offset_y
                    - cell_size
                )

                draw.text(
                    (x_position, y_position), str(number), font=font, fill=(0, 0, 0)
                )

        return max_row_clue_len, max_col_clue_len

    def draw_grid(
        self,
        draw: ImageDraw.Draw,
        cell_size: int,
        offset_x: int,
        offset_y: int,
        solution: bool = False,
    ) -> None:
        for i in range(self.hanjie.N):
            for j in range(self.hanjie.N):
                if solution and self.hanjie.grid[i][j] == 1:
                    top_left = (j * cell_size + offset_x, i * cell_size + offset_y)
                    bottom_right = (
                        (j + 1) * cell_size + offset_x,
                        (i + 1) * cell_size + offset_y,
                    )
                    draw.rectangle([top_left, bottom_right], fill="black")

        for i in range(self.hanjie.N + 1):  # +1 to close the grid
            draw.line(
                [
                    (cell_size * i) + offset_x - 1,
                    offset_y,
                    (cell_size * i) + offset_x - 1,
                    cell_size * self.hanjie.N + offset_y,
                ],
                fill="grey",
            )
            draw.line(
                [
                    offset_x,
                    (cell_size * i) + offset_y - 1,
                    cell_size * self.hanjie.N + offset_x,
                    (cell_size * i) + offset_y - 1,
                ],
                fill="grey",
            )

    def build_image(self, cell_size: int = 30, solution: bool = False) -> Image.Image:
        font = ImageFont.truetype("arial.ttf", cell_size // 2)
        max_row_clue_len: int = max(len(clue) for clue in self.hanjie.row_clues)
        max_col_clue_len: int = max(len(clue) for clue in self.hanjie.col_clues)

        img_width: int = self.hanjie.N * cell_size + max_row_clue_len * cell_size
        img_height: int = self.hanjie.N * cell_size + max_col_clue_len * cell_size

        img = Image.new("RGB", (img_width, img_height), color="white")
        draw = ImageDraw.Draw(img)

        self.draw_clues(
            draw,
            cell_size,
            font,
            max_row_clue_len * cell_size,
            max_col_clue_len * cell_size,
        )
        self.draw_grid(
            draw,
            cell_size,
            max_row_clue_len * cell_size,
            max_col_clue_len * cell_size,
            solution,
        )

        return img

    def to_image(self, filename: str = "hanjie_clues.png") -> None:
        img = self.build_image()
        img.save(filename)
