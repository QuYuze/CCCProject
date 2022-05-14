/* eslint-disable react/prop-types */
import React, { useRef, useEffect, useState } from 'react'
import ReactDOM from 'react-dom'
import mapboxgl from 'mapbox-gl'
import data from 'src/assets/updated_sub.json'
import 'mapbox-gl/dist/mapbox-gl.css'
import { CButton, CCallout } from '@coreui/react'
import { getExample } from '../../api'
import { getMap } from '../../api'
import sushiImage from './foodicons/sushi.png'
import pizzaImage from './foodicons/pizza.png'
import tacoImage from './foodicons/taco.png'
import croissantImage from './foodicons/croissant.png'
import curryImage from './foodicons/curry.png'
import foodImage from './foodicons/food.png'
import hummusImage from './foodicons/hummus.png'
import paellaImage from './foodicons/paella.png'
import saladImage from './foodicons/salad.png'
import tomyumImage from './foodicons/tom-yum.png'
import vegemiteImage from './foodicons/vegemite.png'
//pop up
const Popup = ({ routeName, food }) => (
    <div className="popup">
        <h5 className="route-name">{routeName}</h5>
        <div className="route-metric-row">
            <p className="row-value">Favorite cuisine is {food} cuisine !</p>
        </div>
    </div>
)

mapboxgl.accessToken =
    'pk.eyJ1IjoibHVuYWxpYW5nIiwiYSI6ImNsMmxtY3NvOTBvZTAzbG5xNzQwM2tsaXMifQ.5lgZAlrVz9lZybZTOv6JAQ'
const FoodMap = () => {

    const [example, setExample] = useState([])
    const loadExample = async () => {
        const example = await getMap()
        setExample(example)
        updateSub(example)
    }
    useEffect(() => {
        console.log(example)
    }, [example])

    const ExampleButton = () => {
        return <CButton color="warning" onClick={loadExample}>Refresh data</CButton>
    }

    const mapContainerRef = useRef(null)
    const [map, setMap] = useState(null)
    const popUpRef = useRef(new mapboxgl.Popup({ offset: 15 }))
    const [dataset, setDataset] = useState(data)

    const updateSub = (updateLs) => {
        // const type = typeof updateLs
        console.log(updateLs.length)
        const newDataset = dataset
        for (let i = 0; i < updateLs.length; i++) {
            console.log("index", i)
            // console.log(updateLs[i]['no_offensive'])
            // console.log(newDataset['features'][i]['properties']['no_offend'])
            newDataset['features'][i]['properties']['fav_food'] = updateLs[i]['fav_food']
            setDataset(newDataset)
            map.getSource('food').setData(dataset)
            console.log(i)
        }

    }

    const ConnectButton = () => {
        return <CButton onClick={getExample}>connect</CButton>


    }

    // Initialize map when component mounts
    useEffect(() => {
        const map = new mapboxgl.Map({
            container: mapContainerRef.current,
            style: 'mapbox://styles/mapbox/light-v10',
            center: [144.946457, -37.840935],
            zoom: 10,
        })

        //layer for boundaries
        map.on('load', () => {
            map.addSource('food', {
                type: 'geojson',
                data,
            })

            map.addLayer(
                {
                    id: 'countries',
                    type: 'line',
                    source: 'food',
                    paint: {
                        'line-color': 'silver'
                    },
                },
            )
            //load images
            map.loadImage(sushiImage, (error, image) => {
                if (error) throw error;
                // add image to the active style and make it SDF-enabled
                map.addImage('sushi', image);
            })
            map.loadImage(pizzaImage, (error, image) => {
                if (error) throw error;
                // add image to the active style and make it SDF-enabled
                map.addImage('pizza', image);
            })
            map.loadImage(tacoImage, (error, image) => {
                if (error) throw error;
                // add image to the active style and make it SDF-enabled
                map.addImage('taco', image);
            })
            map.loadImage(croissantImage, (error, image) => {
                if (error) throw error;
                // add image to the active style and make it SDF-enabled
                map.addImage('croissant', image);
            })
            map.loadImage(curryImage, (error, image) => {
                if (error) throw error;
                // add image to the active style and make it SDF-enabled
                map.addImage('curry', image);
            })
            map.loadImage(foodImage, (error, image) => {
                if (error) throw error;
                // add image to the active style and make it SDF-enabled
                map.addImage('food', image);
            })
            map.loadImage(hummusImage, (error, image) => {
                if (error) throw error;
                // add image to the active style and make it SDF-enabled
                map.addImage('hummus', image);
            })
            map.loadImage(paellaImage, (error, image) => {
                if (error) throw error;
                // add image to the active style and make it SDF-enabled
                map.addImage('paella', image);
            })
            map.loadImage(saladImage, (error, image) => {
                if (error) throw error;
                // add image to the active style and make it SDF-enabled
                map.addImage('salad', image);
            })
            map.loadImage(tomyumImage, (error, image) => {
                if (error) throw error;
                // add image to the active style and make it SDF-enabled
                map.addImage('tomyum', image);
            })
            map.loadImage(vegemiteImage, (error, image) => {
                if (error) throw error;
                // add image to the active style and make it SDF-enabled
                map.addImage('vegemite', image);
            })

            map.addLayer(
                // console.log("h"),
                {

                    id: 'marker',
                    type: 'symbol',
                    source: 'food',
                    layout: {
                        'icon-image': [
                            'match',
                            ['get', 'fav_food'], // Use the result 'type' property
                            'Japanese', 'sushi',
                            'Mexican', 'taco',
                            'French', 'croissant',
                            'Indian', 'curry',
                            'Korean', 'food',
                            'Lebanese', 'hummus',
                            'Spanish', 'paella',
                            'Greek', 'salad',
                            'Thai', 'tomyum',
                            'Italian', 'pizza',
                            ''
                        ],
                        'icon-size': 0.5
                    }
                }


            );

            //pop up
            map.on('click', (e) => {
                const features = map.queryRenderedFeatures(e.point, {
                    layers: ['marker'],
                })
                if (features.length > 0) {
                    const feature = features[0]
                    // create popup node
                    const popupNode = document.createElement('div')
                    ReactDOM.render(
                        <Popup
                            routeName={feature?.properties?.name}
                            food={feature?.properties?.fav_food}
                        />,
                        popupNode,
                    )
                    popUpRef.current.setLngLat(e.lngLat).setDOMContent(popupNode).addTo(map)
                }
            })

            setMap(map)
        })

        return () => map.remove();
    }, []);


    return (
        <div>
            <h1>Food Map of Melbourne</h1>
            <CCallout color="dark">
                This map shows people's favorite types of cuisine in different suburbs in Melbourne extracted from Twitter. Click the 'Refresh data' button to see the latest data. Click the food icons on the map to see the suburb's name and its favorite cuisine!
            </CCallout>
            <ExampleButton />
            <div ref={mapContainerRef} className="h600 mt12" />
        </div>
    )
}

export default FoodMap

