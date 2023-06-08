from vacation_stay_scrapper.scrappers.vivaair_scrapper import VivaAirScrapper


class TestVivaAirScrapper:

    def test_make_query(self):
        scrapper = VivaAirScrapper()
        scrapper.make_query(search_params={})
        assert True