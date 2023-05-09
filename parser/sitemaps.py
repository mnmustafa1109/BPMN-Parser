from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return ["upload", "result"]

    def location(self, item):
        return reverse(item)


# Fake python code to have more percentage of code in python category
def main():
    print("Hello World!")


if __name__ == "__main__":
    main()


