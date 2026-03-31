import io
import time
import requests
import pandas as pd
from django.core.management.base import BaseCommand
from stocks.models import Stock


class Command(BaseCommand):
    help = 'Sync all stocks from NSE + Crypto from CoinGecko into the Stock model'

    NSE_URL       = 'https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv'
    COINGECKO_URL = 'https://api.coingecko.com/api/v3/coins/markets'

    def add_arguments(self, parser):
        parser.add_argument('--source', choices=['nse', 'crypto', 'all'], default='all')

    def handle(self, *args, **options):
        source  = options['source']
        created = updated = skipped = 0

        if source in ('nse', 'all'):
            c, u, s = self._sync_nse()
            created += c; updated += u; skipped += s

        if source in ('crypto', 'all'):
            c, u, s = self._sync_crypto()
            created += c; updated += u; skipped += s

        self.stdout.write(self.style.SUCCESS(
            f'\nDone — created: {created}, updated: {updated}, skipped: {skipped}'
        ))

    def _sync_nse(self):
        self.stdout.write('\nFetching NSE EQUITY_L.csv...')
        created = updated = skipped = 0

        try:
            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0'})
            r = session.get(self.NSE_URL, timeout=30)
            r.raise_for_status()
            df = pd.read_csv(io.BytesIO(r.content))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'NSE fetch failed: {e}'))
            return 0, 0, 0

        # THE FIX: strip ALL whitespace from every column name at once
        df.columns = df.columns.str.strip()

        # Filter EQ series only (skip BE, BZ, SM, etc.)
        if 'SERIES' in df.columns:
            df = df[df['SERIES'].str.strip() == 'EQ'].copy()

        self.stdout.write(f'  Columns detected: {list(df.columns)}')
        self.stdout.write(f'  {len(df)} EQ equities found')

        for _, row in df.iterrows():
            symbol = str(row['SYMBOL']).strip() + '.NS'
            name   = str(row['NAME OF COMPANY']).strip().title()

            obj, was_created = Stock.objects.get_or_create(
                symbol=symbol,
                defaults={
                    'name':     name,
                    'exchange': 'NSE',
                    'sector':   '',
                }
            )

            if was_created:
                created += 1
                if created <= 5:
                    self.stdout.write(self.style.SUCCESS(f'  + {symbol:<22} {name[:40]}'))
            else:
                if obj.name != name:
                    obj.name = name
                    obj.save(update_fields=['name'])
                    updated += 1
                else:
                    skipped += 1

        self.stdout.write(f'  NSE: +{created} new, ~{updated} updated, {skipped} skipped')
        return created, updated, skipped

    def _sync_crypto(self):
        self.stdout.write('\nFetching crypto from CoinGecko (top 750)...')
        created = updated = skipped = 0
        all_coins = []

        for page in range(1, 4):
            for attempt in range(3):          # retry up to 3 times
                try:
                    r = requests.get(
                        self.COINGECKO_URL,
                        params={
                            'vs_currency': 'usd',
                            'order':       'market_cap_desc',
                            'per_page':    250,
                            'page':        page,
                            'sparkline':   False,
                        },
                        timeout=30,
                    )
                    r.raise_for_status()
                    batch = r.json()
                    if not batch:
                        break
                    all_coins.extend(batch)
                    self.stdout.write(f'  Page {page}: {len(batch)} coins')
                    time.sleep(8)             # wait 8s between pages — respects rate limit
                    break                     # success — move to next page
                except requests.exceptions.HTTPError as e:
                    if r.status_code == 429:
                        wait = 30 * (attempt + 1)   # 30s, 60s, 90s on each retry
                        self.stdout.write(self.style.WARNING(
                            f'  Rate limited on page {page}. Waiting {wait}s (attempt {attempt+1}/3)...'
                        ))
                        time.sleep(wait)
                    else:
                        self.stdout.write(self.style.WARNING(f'  Page {page} failed: {e}'))
                        break
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  Page {page} error: {e}'))
                    break

        self.stdout.write(f'  Total coins fetched: {len(all_coins)}')

        for coin in all_coins:
            symbol = coin['symbol'].upper() + '-USD'
            name   = coin['name']
            rank   = coin.get('market_cap_rank') or 9999

            obj, was_created = Stock.objects.get_or_create(
                symbol=symbol,
                defaults={
                    'name':     name,
                    'exchange': 'CRYPTO',
                    'sector':   f'Rank #{rank}',
                }
            )

            if was_created:
                created += 1
                if created <= 5:
                    self.stdout.write(self.style.SUCCESS(f'  + {symbol:<14} {name}'))
            else:
                if obj.name != name:
                    obj.name = name
                    obj.save(update_fields=['name'])
                    updated += 1
                else:
                    skipped += 1

        self.stdout.write(f'  Crypto: +{created} new, ~{updated} updated, {skipped} skipped')
        return created, updated, skipped