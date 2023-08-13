import random
from typing import List, Self, Tuple, Union
import concurrent.futures
from PIL import Image


class HanjieBase:
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

    @classmethod
    def from_image(cls, img_path: str, resolution: int, threshold: int = 128) -> Self:
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
