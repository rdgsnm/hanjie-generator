import random
from typing import List, Tuple, Union
from PIL import Image, ImageDraw, ImageFont
import concurrent.futures


class Hanjie:
    def __init__(self, N_or_grid: Union[int, List[List[int]]], fill_prob: float = 0.3):
        self.grid: List[List[int]]

        if isinstance(N_or_grid, int):
            self.N: int = N_or_grid
            self.grid = self.generate_grid(fill_prob)
        else:
            self.grid = N_or_grid
            self.N = len(N_or_grid)

        self.row_clues, self.col_clues = self.compute_clues()

    def generate_grid(self, fill_prob: float) -> List[List[int]]:
        return [
            [1 if random.random() < fill_prob else 0 for _ in range(self.N)]
            for _ in range(self.N)
        ]

    def compute_clues(self) -> Tuple[List[List[int]], List[List[int]]]:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            row_clues: List[List[int]] = list(
                executor.map(self.compute_clue_from_line, self.grid)
            )

        transposed_grid = list(zip(*self.grid))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            col_clues: List[List[int]] = list(
                executor.map(self.compute_clue_from_line, transposed_grid)
            )

        return row_clues, col_clues

    @staticmethod
    def compute_clue_from_line(line: List[int]) -> List[int]:
        clue: List[int] = []
        count: int = 0

        for cell in line:
            if cell == 1:
                count += 1
            elif count:
                clue.append(count)
                count = 0

        if count:
            clue.append(count)

        return clue if clue else [0]

    def print_solution(self) -> None:
        for row in self.grid:
            print("".join("#" if cell else "." for cell in row))

    def draw_clues(
        self,
        draw: ImageDraw.Draw,
        cell_size: int,
        font: ImageFont.FreeTypeFont,
        offset_x: int,
        offset_y: int,
    ) -> Tuple[int, int]:
        max_row_clue_len: int = max(len(clue) for clue in self.row_clues)
        max_col_clue_len: int = max(len(clue) for clue in self.col_clues)

        for i, clue in enumerate(self.row_clues):
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

        for i, clue in enumerate(self.col_clues):
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
        for i in range(self.N):
            for j in range(self.N):
                if solution and self.grid[i][j] == 1:
                    top_left = (j * cell_size + offset_x, i * cell_size + offset_y)
                    bottom_right = (
                        (j + 1) * cell_size + offset_x,
                        (i + 1) * cell_size + offset_y,
                    )
                    draw.rectangle([top_left, bottom_right], fill="black")

        for i in range(self.N + 1):  # +1 to close the grid
            draw.line(
                [
                    (cell_size * i) + offset_x - 1,
                    offset_y,
                    (cell_size * i) + offset_x - 1,
                    cell_size * self.N + offset_y,
                ],
                fill="grey",
            )
            draw.line(
                [
                    offset_x,
                    (cell_size * i) + offset_y - 1,
                    cell_size * self.N + offset_x,
                    (cell_size * i) + offset_y - 1,
                ],
                fill="grey",
            )

    def build_image(self, cell_size: int = 30, solution: bool = False) -> Image.Image:
        font = ImageFont.truetype("arial.ttf", cell_size // 2)
        max_row_clue_len: int = max(len(clue) for clue in self.row_clues)
        max_col_clue_len: int = max(len(clue) for clue in self.col_clues)

        img_width: int = self.N * cell_size + max_row_clue_len * cell_size
        img_height: int = self.N * cell_size + max_col_clue_len * cell_size

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

    @classmethod
    def from_image(
        cls, img_path: str, resolution: int, threshold: int = 128
    ) -> "Hanjie":
        img = Image.open(img_path).convert("L")  # Convert to grayscale

        # Convert palette images with transparency to RGBA
        if img.mode == "P":
            img = img.convert("RGBA")

        aspect_ratio: float = img.width / img.height
        if img.width > img.height:
            new_width = resolution
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = resolution
            new_width = int(new_height * aspect_ratio)

        img = img.resize((new_width, new_height), Image.LANCZOS)

        pixels: List[int] = list(img.getdata())
        grid: List[List[int]] = [[0] * new_width for _ in range(new_height)]

        for i in range(new_height):
            for j in range(new_width):
                grid[i][j] = 1 if pixels[i * new_width + j] < threshold else 0

        return cls(grid)
