'use strict';
import {GET_INFOBOX_DONE, GET_COUNTRIES_DONE, DRAG_END_POLYGON, DRAG_END_POLYGON_FAIL, GIVE_UP} from '../actions';


function moveTo(paths, latLng) {
    let polygon = new google.maps.Polygon({geodesic: true, paths: paths});
    polygon.moveTo(latLng);
    return polygon.getPaths();
}


function extractPolygons(countries) {
    return countries.map(country => {
        let originalPath = country.polygon.map(polygon => (google.maps.geometry.encoding.decodePath(polygon)));
        return {
            id: country.id,
            draggable: true,
            isSolved: false,
            infobox: {},
            paths: moveTo(
                originalPath,
                new google.maps.LatLng(country.default_position[1], country.default_position[0])),
            originalPath: originalPath,
            answer: new google.maps.LatLngBounds(
                new google.maps.LatLng(country.answer[0][1], country.answer[0][0]),
                new google.maps.LatLng(country.answer[1][1], country.answer[1][0])),
        }
    });
}


const polygons = (state = [], action) => {
    switch (action.type) {
        case GET_INFOBOX_DONE:
            return state.map((country) => {
                if (country.id === action.id) {
                    return {...country, infobox: action.data};
                }
                return country
            });
        case GET_COUNTRIES_DONE:
            return extractPolygons(action.countries);
        case GIVE_UP:
            return state.map((polygon) => {
                    if (!polygon.isSolved) {
                        return {...polygon,
                            draggable: false,
                            paths: polygon.originalPath,
                        };
                    }
                    return polygon
                });
        case DRAG_END_POLYGON_FAIL:
            return state.map((polygon) => {
                    if (polygon.id === action.id) {
                        return {...polygon, paths: action.paths};
                    }
                    return polygon
                });
        case DRAG_END_POLYGON:
            return state.map((polygon) => {
                    if (polygon.id === action.id) {
                        return {...polygon,
                            draggable: false,
                            isSolved: true,
                            paths: polygon.originalPath,
                        };
                    }
                    return polygon
                });
        default:
            return state
    }
};


export default polygons