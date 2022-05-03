import React, { useRef, useEffect, useState } from 'react'
import mapboxgl from '!mapbox-gl' // eslint-disable-line import/no-webpack-loader-syntax
import 'src/scss/map.css'
import data from 'src/assets/cdata/stest.json'
import Legend from 'src/components/mapCompo/Legend';
import Optionsfield from 'src/components/mapCompo/Optionsfield';
//import { DocsCallout } from 'src/components'
mapboxgl.accessToken = 'pk.eyJ1IjoibHVuYWxpYW5nIiwiYSI6ImNsMmxtY3NvOTBvZTAzbG5xNzQwM2tsaXMifQ.5lgZAlrVz9lZybZTOv6JAQ';


const Map = () => {
  const mapContainerRef = useRef(null)
  // const map = useRef(null)
  const [lng, setLng] = useState(144.946457)
  const [lat, setLat] = useState(-37.840935)
  const [zoom, setZoom] = useState(10)
  const [map, setMap] = useState(null);
  // const [map, setMap] = useState(null);

  const options = [
    {
      name: 'no_offensive',
      description: 'number of offensive tweets',
      property: 'no_offend',
      stops: [
        [0, '#f8d5cc'],
        [5, '#f4bfb6'],
        [10, '#f1a8a5'],
        [15, '#ee8f9a'],
        [50000000, '#ec739b'],
        [100000000, '#dd5ca8'],
        [250000000, '#c44cc0'],
        [500000000, '#9f43d7'],
        [1000000000, '#6e40e6']
      ]

    },
    {
      name: 'GDP',
      description: 'Estimate total GDP in millions of dollars',
      property: 'gdp_md_est',
      stops: [
        [0, '#f8d5cc'],
        [1000, '#f4bfb6'],
        [5000, '#f1a8a5'],
        [10000, '#ee8f9a'],
        [50000, '#ec739b'],
        [100000, '#dd5ca8'],
        [250000, '#c44cc0'],
        [5000000, '#9f43d7'],
        [10000000, '#6e40e6']
      ]
    }
  ];
  const [active, setActive] = useState(options[0]);

  useEffect(() => {
    // if (map.current) return; // initialize map only once
    // map.current = new mapboxgl.Map({
    //   container: mapContainer.current,
    //   style: 'mapbox://styles/mapbox/streets-v11',
    //   center: [lng, lat],
    //   zoom: zoom
    // });
    // if (!map.current) return; // wait for map to initialize
    // map.current.on('move', () => {
    //   setLng(map.current.getCenter().lng.toFixed(4));
    //   setLat(map.current.getCenter().lat.toFixed(4));
    //   setZoom(map.current.getZoom().toFixed(2));
    // });
    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [lng, lat],
      zoom: zoom
    });

    map.on('load', () => {
      map.addSource('stest', {
        type: 'geojson',
        data: data
      });
      console.log(data)
      map.setLayoutProperty('suburb-label', 'text-field', [
        'format',
        ['get', 'name'],
        { 'font-scale': 1.2 },
        // '\n',
        // {},
        // ['get', 'name'],
        // {
        //   'font-scale': 0.8,
        //   'text-font': [
        //     'literal',
        //     ['DIN Offc Pro Italic', 'Arial Unicode MS Regular']
        //   ]
        // }
      ]);
      map.addLayer(
        {
          id: 'stest',
          type: 'line',
          source: 'stest'
        },
        'suburb-label'
      );
      console.log(active.property)
      map.setPaintProperty('stest', 'fill-color', ['match', ['get', 'no_offend']]);
      // map.setPaintProperty('stest', 'fill-color', {
      //   property: active.property,
      //   stops: active.stops
      // });
      // console("setpaint")
      setMap(map);

    });
    // map.current.addLayer(
    //   {
    //     id: 'stest',
    //     type: 'fill',
    //     source: 'stest'
    //   });

    return () => map.remove();
  }, []);

  // });

  // map.on('load', () => {
  //   map.addLayer({
  //     id: 'terrain-data',
  //     type: 'line',
  //     source: {
  //       type: 'vector',
  //       url: 'mapbox://mapbox.mapbox-terrain-v2'
  //     },
  //     'source-layer': 'contour'
  //   });
  // });

  // useEffect(() => {
  //   if (map.current) return; // initialize map only once
  //   map.current = new mapboxgl.Map({
  //     container: mapContainer.current,
  //     style: 'mapbox://styles/mapbox/streets-v11',
  //     center: [lng, lat],
  //     zoom: zoom
  //   });
  // })

  useEffect(() => {
    paint();
  }, [active]);

  const paint = () => {
    console.log("paint")
    if (map) {
      map.setPaintProperty('stest', 'fill-color', {
        property: active.property,
        stops: active.stops
      });
    }

    console.log("pass")
  };

  const changeState = i => {
    setActive(options[0]);
    map.setPaintProperty('stest', 'fill-color', {
      property: active.property,
      stops: active.stops
    });
  };
  console.log('hi')

  return (
    <div>
      <div className="sidebar">
        Longitude: {lng} | Latitude: {lat} | Zoom: {zoom}
      </div>
      <div ref={mapContainerRef} className="map-container" />
      <Legend active={active} stops={active.stops} />
      <Optionsfield
        options={options}
        property={active.property}
        changeState={changeState}
      />
    </div>
  );
};

export default Map;