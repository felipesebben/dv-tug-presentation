<?xml version='1.0'?>

<!--
  Custom colour palettes for the V2 dashboard.
  Token definitions and the reasoning behind them: docs/dashboard_v2_design_system.md

  To install: copy this file to
      Documents/My Tableau Repository/Preferences.tps
      (pt-BR: Documentos/Meu repositório do Tableau/Preferences.tps)
  overwriting any existing file, then restart Tableau Desktop. The palettes then
  appear by name in Marks -> Color -> Edit Colors.

  Every value here was validated with a CVD simulator, not chosen by eye. The
  blue/orange highlight pair scores 24.7 dE under protanopia; the green/orange pair
  originally suggested in docs/uxers_guidance.md scores 3.2 and was rejected.
-->

<workbook>
    <preferences>

        <!-- Default working palette: grey is the default, colour is the exception.
             Slot 1 is every mark that is NOT making the argument. -->
        <color-palette name="V2 Neutro e Destaque" type="regular">
            <color>#8c8c89</color>
            <color>#2a78d6</color>
            <color>#eb6834</color>
        </color-palette>

        <!-- Two-series case only (e.g. capacity vs demand, indexed to 2019 = 100). -->
        <color-palette name="V2 Destaque" type="regular">
            <color>#2a78d6</color>
            <color>#eb6834</color>
        </color-palette>

        <!-- Bed types: one hue in ordered tones. Max 4 categories + "Outros" (#8c8c89).
             Validated ordinal: monotone lightness, step gaps >= 0.06, light end 2.11:1. -->
        <color-palette name="V2 Leitos" type="ordered-sequential">
            <color>#86b6ef</color>
            <color>#3987e5</color>
            <color>#256abf</color>
            <color>#184f95</color>
        </color-palette>

        <!-- Choropleth / magnitude. Single hue, light = low.
             Replaces V1's green-yellow-red divergent map. -->
        <color-palette name="V2 Sequencial Azul" type="ordered-sequential">
            <color>#cde2fb</color>
            <color>#9ec5f4</color>
            <color>#6da7ec</color>
            <color>#3987e5</color>
            <color>#256abf</color>
            <color>#184f95</color>
            <color>#0d366b</color>
        </color-palette>

    </preferences>
</workbook>
