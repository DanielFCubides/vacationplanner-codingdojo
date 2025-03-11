% colombia_tourism.pl
% Knowledge base for Colombian cities and tourism

% City Characteristics
% Weather
warm(cartagena).
warm(barranquilla).
warm(santa_marta).
warm(cali).
moderate(medellin).
moderate(bogota).
cold(bogota).

% Geographical Features
beach(cartagena).
beach(santa_marta).
beach(barranquilla).
mountain(medellin).
mountain(bogota).
valley(cali).
river(barranquilla).

% Cultural Aspects
historicCity(cartagena).
historicCity(bogota).
historicCity(santa_marta).
modernCity(medellin).
modernCity(bogota).
modernCity(barranquilla).

% Tourism Types
culturalTourism(cartagena).
culturalTourism(bogota).
culturalTourism(medellin).
beachTourism(cartagena).
beachTourism(santa_marta).
beachTourism(barranquilla).
businessTourism(bogota).
businessTourism(medellin).
businessTourism(barranquilla).
ecoTourism(santa_marta).
ecoTourism(medellin).
ecoTourism(cali).

% City Attractions
hasAttraction(cartagena, walled_city).
hasAttraction(cartagena, beaches).
hasAttraction(bogota, gold_museum).
hasAttraction(bogota, monserrate).
hasAttraction(medellin, metro_cable).
hasAttraction(medellin, parque_arvi).
hasAttraction(santa_marta, tayrona_park).
hasAttraction(santa_marta, rodadero).
hasAttraction(barranquilla, carnival).
hasAttraction(cali, salsa_dancing).
hasAttraction(cali, zoo).

% Search History
% Format: userSearch(UserId, City, Date)
userSearch(user1, cartagena, '2024-02-15').
userSearch(user1, santa_marta, '2024-02-15').
userSearch(user2, bogota, '2024-02-14').
userSearch(user2, medellin, '2024-02-14').
userSearch(user3, cali, '2024-02-13').
userSearch(user3, cartagena, '2024-02-13').

% City Similarity Rules

% Weather Similarity
weatherSimilar(City1, City2) :-
    City1 \= City2,
    (
        (warm(City1), warm(City2));
        (moderate(City1), moderate(City2));
        (cold(City1), cold(City2))
    ).

% Geography Similarity
geographySimilar(City1, City2) :-
    City1 \= City2,
    (
        (beach(City1), beach(City2));
        (mountain(City1), mountain(City2));
        (valley(City1), valley(City2));
        (river(City1), river(City2))
    ).

% Tourism Type Similarity
tourismSimilar(City1, City2) :-
    City1 \= City2,
    (
        (culturalTourism(City1), culturalTourism(City2));
        (beachTourism(City1), beachTourism(City2));
        (businessTourism(City1), businessTourism(City2));
        (ecoTourism(City1), ecoTourism(City2))
    ).

% Overall Similarity Score
% Cities are similar if they share at least two characteristics
similarCities(City1, City2, Score) :-
    City1 \= City2,
    findall(1, weatherSimilar(City1, City2), WeatherMatches),
    findall(1, geographySimilar(City1, City2), GeoMatches),
    findall(1, tourismSimilar(City1, City2), TourismMatches),
    length(WeatherMatches, W),
    length(GeoMatches, G),
    length(TourismMatches, T),
    Score is W + G + T.

% Recommend similar cities
recommendSimilar(City, RecommendedCity) :-
    similarCities(City, RecommendedCity, Score),
    Score > 0.

% Find users who searched for similar cities
findRelatedUsers(City, User) :-
    userSearch(User, City, _),
    userSearch(User, OtherCity, _),
    City \= OtherCity,
    similarCities(City, OtherCity, Score),
    Score >= 2.

% Example queries:
% Find similar cities to Cartagena:
% ?- recommendSimilar(cartagena, X).

% Find users who searched for similar cities:
% ?- findRelatedUsers(cartagena, X).

% Find cities with specific characteristics:
% ?- beach(X), culturalTourism(X).

% Find similarity score between two cities:
% ?- similarCities(cartagena, santa_marta, Score).
