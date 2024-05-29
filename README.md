# Simple monitor the Azure AI Proxy

[Azure AI Proxy](https://github.com/microsoft/azure-openai-service-proxy/)

## Network Manager

Code for the network manager can be found in the [Pimoroni MicroPython Commmon folder](https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/common)

## Notes

The app forces garbage collection after most operations. This is required for requests.get https calls which use and fragment the limited memory on the microcontroller.
