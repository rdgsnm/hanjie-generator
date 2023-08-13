import requests
from PIL import Image
from io import BytesIO
from hanjie import Hanjie


class PixelArtHanjie:
    def __init__(self, urls):
        self.urls = urls
        self.hanjie_objects = []
        self.fetch_and_generate_hanjie()

    def fetch_and_generate_hanjie(self):
        for url in self.urls:
            response = requests.get(url)
            image_data = BytesIO(response.content)
            hanjie = Hanjie.from_image(
                image_data, resolution=25, threshold=128
            )  # Assuming a resolution of 50 for demonstration
            self.hanjie_objects.append(hanjie)

    def save_all_hanjie_in_one_pdf(self, filename="Hanjie_Collection.pdf"):
        clues_images = []
        solutions_images = []

        for hanjie in self.hanjie_objects:
            clues_images.append(hanjie.build_image(solution=False))
            solutions_images.append(hanjie.build_image(solution=True))

        # Combine clue images and solution images in the order of appearance
        all_images = clues_images + solutions_images

        # Save to a single PDF
        clues_images[0].save(
            filename,
            save_all=True,
            append_images=all_images[1:],
            resolution=100.0,
            quality=95,
            optimize=True,
        )


pixel_art_url = [
    "https://banner2.cleanpng.com/20180802/zgy/kisspng-the-legend-of-zelda-a-link-to-the-past-the-legend-link-pixel-art-24x24-bing-images-5b62ce943e5e08.0500365515332020682555.jpg",
    "https://www.vhv.rs/dpng/d/446-4468602_stardew-valley-chicken-pixel-art-hd-png-download.png",
    "https://e7.pngegg.com/pngimages/910/545/png-clipart-heart-pixel-art-pixel-flag-text-thumbnail.png",
    "https://i0.wp.com/alicekeeler.com/wp-content/uploads/2015/05/Screen-Shot-2015-05-23-at-7.39.40-AM.png?fit=504%2C494&ssl=1",
]
pixel_art_hanjie = PixelArtHanjie(pixel_art_url)
pixel_art_hanjie.save_all_hanjie_in_one_pdf()
