#! /bin/bash

DOMAIN='http://openag-abfcdeca.serveo.net'
curl -u openag:openag -d '{"recipient":{"type": "Peripheral", "name": "IndicatorLEDs"}, "request":{"type":"Set User LED", "value":"Blue"}}' -H "Content-Type: application/json" $DOMAIN/api/event/
