from django.core.management.base import BaseCommand, CommandError

from integrations.ads_api_client import AdsAPIError
from real_estate.services import sync_ads_listings


class Command(BaseCommand):
    help = "Synchronize properties from ADS-API into the local database."

    def add_arguments(self, parser):
        parser.add_argument("--city", dest="city", type=str, help="City filter", default=None)
        parser.add_argument("--price-min", dest="price_min", type=int, default=None)
        parser.add_argument("--price-max", dest="price_max", type=int, default=None)
        parser.add_argument("--startid", dest="startid", type=int, default=None)
        parser.add_argument("--limit", dest="limit", type=int, default=200)

    def handle(self, *args, **options):
        try:
            summary = sync_ads_listings(
                city=options.get("city"),
                price_min=options.get("price_min"),
                price_max=options.get("price_max"),
                startid=options.get("startid"),
                limit=options.get("limit"),
            )
        except AdsAPIError as exc:
            raise CommandError(str(exc))

        self.stdout.write(
            self.style.SUCCESS(
                "ADS sync finished: created={created}, updated={updated}, total={total}, skipped={skipped}".format(
                    **summary
                )
            )
        )
