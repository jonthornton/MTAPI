## Endpoints

- **/by-location?lat=[latitude]&lon=[longitude]**  
Returns the 5 stations nearest the provided lat/lon pair.
```javascript
{
    "data": [
        {
            "N": [
                {
                    "route": "6",
                    "time": "2014-08-29T14:00:55-04:00"
                },
                {
                    "route": "6X",
                    "time": "2014-08-29T14:10:30-04:00"
                },
                ...
            ],
            "S": [
                {
                    "route": "6",
                    "time": "2014-08-29T14:04:14-04:00"
                },
                {
                    "route": "6",
                    "time": "2014-08-29T14:11:07-04:00"
                },
                ...
            ],
            "hasData": true,
            "id": 123,
            "location": [
                40.725606,
                -73.9954315
            ],
            "name": "Broadway-Lafayette St / Bleecker St",
            "routes": [
                "6X",
                "6"
            ],
            "stops": {
                "637": [
                    40.725915,
                    -73.994659
                ],
                "D21": [
                    40.725297,
                    -73.996204
                ]
            }
        },
        {
            "N": [
                {
                    "route": "6X",
                    "time": "2014-08-29T14:09:30-04:00"
                },
                {
                    "route": "6",
                    "time": "2014-08-29T14:13:30-04:00"
                },
                ...
            ],
            "S": [
                {
                    "route": "6",
                    "time": "2014-08-29T14:05:14-04:00"
                },
                {
                    "route": "6",
                    "time": "2014-08-29T14:12:07-04:00"
                },
                ...
            ],
            "hasData": true,
            "id": 124,
            "location": [
                40.723315,
                -73.9974215
            ],
            "name": "Spring St / Prince St",
            "routes": [
                "6X",
                "6"
            ],
            "stops": {
                "638": [
                    40.722301,
                    -73.997141
                ],
                "R22": [
                    40.724329,
                    -73.997702
                ]
            }
        },
        ...
    ],
    "updated": "2014-08-29T15:27:27-04:00"
}
```

- **/by-route/[route]**  
Returns all stations on the provided train route.  
```javascript
{
    "data": [
        {
            "N": [
                {
                    "route": "6X",
                    "time": "2014-08-29T14:01:54-04:00"
                },
                {
                    "route": "5",
                    "time": "2014-08-29T14:04:35-04:00"
                },
                {
                    "route": "4",
                    "time": "2014-08-29T14:07:00-04:00"
                },
                ...
            ],
            "S": [
                {
                    "route": "6",
                    "time": "2014-08-29T14:01:53-04:00"
                },
                {
                    "route": "4",
                    "time": "2014-08-29T14:04:52-04:00"
                },
                ...
            ],
            "hasData": true,
            "id": 12,
            "location": [
                40.804138,
                -73.937594
            ],
            "name": "125 St",
            "routes": [
                "6X",
                "5",
                "4",
                "6"
            ],
            "stops": {
                "621": [
                    40.804138,
                    -73.937594
                ]
            }
        },
        {
            "N": [
                {
                    "route": "5",
                    "time": "2014-08-29T14:07:05-04:00"
                },
                {
                    "route": "4",
                    "time": "2014-08-29T14:09:30-04:00"
                },
                ...
            ],
            "S": [
                {
                    "route": "4",
                    "time": "2014-08-29T14:02:22-04:00"
                },
                {
                    "route": "5",
                    "time": "2014-08-29T14:03:36-04:00"
                },
                ...
            ],
            "hasData": true,
            "id": 123,
            "location": [
                40.813224,
                -73.929849
            ],
            "name": "138 St - Grand Concourse",
            "routes": [
                "5",
                "4"
            ],
            "stops": {
                "416": [
                    40.813224,
                    -73.929849
                ]
            }
        },
        ...
    ],
    "updated": "2014-08-29T15:25:27-04:00"
}
```

- **/by-id/[id],[id],[id]...**  
Returns the stations with the provided IDs, in the order provided. IDs should be comma separated with no space characters.

- **/routes**  
Lists available routes.  
```javascript
{
    "data": [
        "S",
        "L",
        "1",
        "3",
        "2",
        "5",
        "4",
        "6",
        "6X"
    ],
    "updated": "2014-08-29T15:09:57-04:00"
}
```