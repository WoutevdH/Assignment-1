## FF AAN HET PRUTSEN NIKS MEE DOEN


from data_loader import *

(
    flight_numbers,
    origin_dict,
    destination_dict,
    departure_time_dict,
    ready_time_dict,
    capacity_dict,
) = mix_flow_flights_loader()

(
    itinerary,
    itinerary_origin_dict,
    itinerary_destination_dict,
    itinerary_flight_1_dict,
    itinerary_flight_2_dict,
    itinerary_price_dict,
    itinerary_demand_dict,
) = mix_flow_itineraries_loader()

recapture_from, recapture_to, recapture_dict = mix_flow_recapture_loader()

path_indexes_with_recapture = {
    (recapture_from[i], recapture_to[i]) for i in recapture_from.keys()
}
# print(path_indexes_with_recapture)

print(recapture_dict.keys())
