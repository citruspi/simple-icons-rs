## simple-icons-rs

[Simple Icons][offical_homepage] support for [Rust][rust_homepage].

API matches that of the [official JavaScript library][official_js_lib_git].

> N.B. The crate is generated on a regular basis and should theoretically match (data and version-wise) the [official library on NPM][official_js_lib_npm].

![pipeline][pipeline_status]

```toml
# Cargo.toml

[dependencies]
simple-icons = "2.9.0"
```

```rust
>>> use simple_icons;
>>> println!(simple_icons::get("apple").unwrap());
Icon {
    title: "Apple",
    slug: "apple",
    hex: "999999",
    source: "https://worldvectorlogo.com/logo/apple",
    svg: "<svg role=\"img\" viewBox=\"0 0 24 24\" xmlns=\"http://www.w3.org/2000/svg\"><title>Apple icon</title><path d=\"M7.078 23.55c-.473-.316-.893-.703-1.244-1.15-.383-.463-.738-.95-1.064-1.454-.766-1.12-1.365-2.345-1.78-3.636-.5-1.502-.743-2.94-.743-4.347 0-1.57.34-2.94 1.002-4.09.49-.9 1.22-1.653 2.1-2.182.85-.53 1.84-.82 2.84-.84.35 0 .73.05 1.13.15.29.08.64.21 1.07.37.55.21.85.34.95.37.32.12.59.17.8.17.16 0 .39-.05.645-.13.145-.05.42-.14.81-.31.386-.14.692-.26.935-.35.37-.11.728-.21 1.05-.26.39-.06.777-.08 1.148-.05.71.05 1.36.2 1.94.42 1.02.41 1.843 1.05 2.457 1.96-.26.16-.5.346-.725.55-.487.43-.9.94-1.23 1.505-.43.77-.65 1.64-.644 2.52.015 1.083.29 2.035.84 2.86.387.6.904 1.114 1.534 1.536.31.21.582.355.84.45-.12.375-.252.74-.405 1.1-.347.807-.76 1.58-1.25 2.31-.432.63-.772 1.1-1.03 1.41-.402.48-.79.84-1.18 1.097-.43.285-.935.436-1.452.436-.35.015-.7-.03-1.034-.127-.29-.095-.576-.202-.856-.323-.293-.134-.596-.248-.905-.34-.38-.1-.77-.148-1.164-.147-.4 0-.79.05-1.16.145-.31.088-.61.196-.907.325-.42.175-.695.29-.855.34-.324.096-.656.154-.99.175-.52 0-1.004-.15-1.486-.45zm6.854-18.46c-.68.34-1.326.484-1.973.436-.1-.646 0-1.31.27-2.037.24-.62.56-1.18 1-1.68.46-.52 1.01-.95 1.63-1.26.66-.34 1.29-.52 1.89-.55.08.68 0 1.35-.25 2.07-.228.64-.568 1.23-1 1.76-.435.52-.975.95-1.586 1.26z\"/></svg>",
    path: "M7.078 23.55c-.473-.316-.893-.703-1.244-1.15-.383-.463-.738-.95-1.064-1.454-.766-1.12-1.365-2.345-1.78-3.636-.5-1.502-.743-2.94-.743-4.347 0-1.57.34-2.94 1.002-4.09.49-.9 1.22-1.653 2.1-2.182.85-.53 1.84-.82 2.84-.84.35 0 .73.05 1.13.15.29.08.64.21 1.07.37.55.21.85.34.95.37.32.12.59.17.8.17.16 0 .39-.05.645-.13.145-.05.42-.14.81-.31.386-.14.692-.26.935-.35.37-.11.728-.21 1.05-.26.39-.06.777-.08 1.148-.05.71.05 1.36.2 1.94.42 1.02.41 1.843 1.05 2.457 1.96-.26.16-.5.346-.725.55-.487.43-.9.94-1.23 1.505-.43.77-.65 1.64-.644 2.52.015 1.083.29 2.035.84 2.86.387.6.904 1.114 1.534 1.536.31.21.582.355.84.45-.12.375-.252.74-.405 1.1-.347.807-.76 1.58-1.25 2.31-.432.63-.772 1.1-1.03 1.41-.402.48-.79.84-1.18 1.097-.43.285-.935.436-1.452.436-.35.015-.7-.03-1.034-.127-.29-.095-.576-.202-.856-.323-.293-.134-.596-.248-.905-.34-.38-.1-.77-.148-1.164-.147-.4 0-.79.05-1.16.145-.31.088-.61.196-.907.325-.42.175-.695.29-.855.34-.324.096-.656.154-.99.175-.52 0-1.004-.15-1.486-.45zm6.854-18.46c-.68.34-1.326.484-1.973.436-.1-.646 0-1.31.27-2.037.24-.62.56-1.18 1-1.68.46-.52 1.01-.95 1.63-1.26.66-.34 1.29-.52 1.89-.55.08.68 0 1.35-.25 2.07-.228.64-.568 1.23-1 1.76-.435.52-.975.95-1.586 1.26z",
}
```


## Usage & API
As noted above, usage of `simple-icons-rs` is very similar to that of the official library with the exception of the icon identifiers (described in the next section).

```rust
use simple_icons;

fn main() {
    let icon = simple_icons::get("Apple");

    match icon {
        Some(i) => println!(i),
        None => println!("no matching icon"),
    }
}
```

As you can see, `get` accepts an icon title and returns an `Option<Icon>`. However, if you compile this code, you might notice that the resulting binary... is nearly 5 MB. That's pretty fucking huge, especially if you only plan to use a handful of icons.

If you know which icons you plan to use at compile time, you can directly import and reference it to reduce your output size.

```rust
use simple_icons;

fn main() {
    println!(simple_icons::icons::Apple);
}
```

Compiling and running this code will print the same information, but the output size is reduced to ~250 KB &mdash; nearly 95% smaller than the previous output size. 


## Identifiers
In the official library, icons are referenced by title in `get` or by their slug for individual imports.

So, e.g. 1Password becomes `1password` and `.NET` becomes `dot-net`.

These can be used within the official library like so:

```javascript
const simpleIcons = require('simple-icons');

console.log(simpleIcons.get('.NET'));

// or

const icon = require('simple-icons/icons/dot-net');

console.log(icon);
```

`simple-icons-rs` is a little different because we can't use those same slugs as valid identifiers within Rust (dashes, numerals, etc. are invalid).

A few examples of identifiers within `simple-icons-rs`

| Title (JavaScript + Rust) | Slug (JavaScript) | Module (Rust) | Struct (Rust) |
|:-|:-|:-|:-|
| `.NET` | `dot-net` | `dot_net` | `DotNet` |
| `1001Tracklists` | `1001tracklists` | `onethousandandone_tracklists` | `OneThousandAndOneTracklists` |
| `1Password` | `1password` | `one_password` | `OnePassword` |
| `500px` | `500px` | `fivehundred_px` | `FiveHundredPx` |
| `A-Frame` | `a-frame` | `a_frame` | `AFrame` |
| `Apple` | `apple` | `apple` | `apple` | 
| `AT&T` | `at-and-t` | `at_and_t` | `ATAndT` |
| `D3.js` | `d3-dot-js` | `d_three_dot_js` | `DThreeDotJs` |
| `iFixit` | `ifixit` | `ifixit` | `IFixit` |
| `Nintendo 3DS` | `nintendo3ds` | `nintendo_three_ds` | `NintendoThreeDS` |
| `Picarto.TV` | `picarto-dot-tv` | `picarto_dot_tv` | `PicartoDotTV` |
| `PlayStation 4` | `playstation4` | `playstation_four` | `PlayStationFour` |
| `Skype for Business` | `skypeforbusiness` | `skype_for_business` | `SkypeForBusiness` |
| `styled-components` | `styled-components` | `styled_components` | `StyledComponents` |
| `TELE5` | `tele5` | `tele_five` | `TELEFive` |
| `Tencent QQ` | `tencentqq` | `tencent_qq` | `TencentQQ` |
| `Wii U` | `wiiu` | `wii_u` | `WiiU` |
| `Windows 95` | `windows95` | `windows_ninety_five` | `WindowsNinetyFive` |


## License
TBH kinda unsure. 

The code in this repository that is used to generate the [crate][crates_io_page] is licensed under [The Unlicense][unlicense] but the official library (which is used to generate the crate) is licensed under [CC0 1.0][cc0] and so I've licensed the crate as such.

In practice I _think_ they should be fairly similar, they're both dedications to the public domain, but IANAL and I haven't done a "legal diff" of the two licenses.


[offical_homepage]: https://simpleicons.org
[official_js_lib_git]: https://github.com/simple-icons/simple-icons
[official_js_lib_npm]: https://npmjs.org/simple-icons
[rust_homepage]: https://www.rust-lang.org
[crates_io_page]: https://crates.io/simple_icons
[unlicense]: https://unlicense.org
[cc0]: https://creativecommons.org/publicdomain/zero/1.0/
[pipeline_status]: https://src.doom.fm/citruspi/simple-icons-rs/badges/master/pipeline.svg