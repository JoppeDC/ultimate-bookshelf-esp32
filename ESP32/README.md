# Ultimate Bookshelf - ESP32

A lightweight WiFi-enabled controller for WS2812B (or similar) addressable LED strips, built with an ESP32. It provides a simple HTTP API to control individual LEDs or entire strips.

This project uses [PlatformIO](https://platformio.org/) for dependency and build management.

## ✨ Features

* Connects to WiFi and hosts a local HTTP API
* Set all LEDs to a uniform color and brightness
* Control individual LEDs via batch commands

## 💠 Hardware Requirements

* ESP32 board
* WS2812B (or FASTLED compatible) LED strip
* 5V power supply (adequate for your LED count)

## 🔧 Configuration

### `include/config.h`

Contains LED strip configuration: pin, number of LEDs, etc.

### `include/secrets.h`

Set your WiFi credentials here.
Use the provided `secrets.h.dist` file as a template.

## 🚀 API Endpoints

### `POST /set_all`

Set all LEDs to the same RGB color and opacity.

#### Request Body

```json
{
  "r": 255,
  "g": 255,
  "b": 255,
  "a": 100
}
```

* `r`, `g`, `b`: Color components (0–255)
* `a`: Opacity as a percentage (0–100)

---

### `POST /set_led`

Set specific LEDs using a batch of instructions.

#### Request Body

```json
[
  { "led": 0, "r": 255, "g": 0, "b": 0, "a": 100 },
  { "led": 1, "r": 0, "g": 255, "b": 0, "a": 80 },
  { "led": 2, "r": 0, "g": 0, "b": 255, "a": 60 }
]
```

* `led`: Index of the LED to modify
* `r`, `g`, `b`, `a`: Same as above

> Opacity (`a`) is scaled to brightness from 0% to 100%

---

## License

MIT
