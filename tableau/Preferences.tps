<?xml version='1.0'?>

<!--
  Custom colour palettes for the V2 dashboard.
  Token definitions and the reasoning behind them: docs/v2/design_system.md

  To install: copy this file to
      Documents/My Tableau Repository/Preferences.tps
      (pt-BR: Documentos/Meu repositório do Tableau/Preferences.tps)
  overwriting any existing file, then restart Tableau Desktop. The palettes then
  appear by name in Marks -> Color -> Edit Colors.

  Every value here was validated with a CVD simulator, not chosen by eye. The
  blue/orange highlight pair scores 24.7 dE under protanopia; the green/orange pair
  originally suggested in docs/foundations/uxers_guidance.md scores 3.2 and was rejected.

  The two colours have different jobs, and the split matters more than the hexes:
      blue   #2a78d6  the data family - default series, and the parent hue of both
                      ramps below. Appears often.
      orange #eb6834  the accent. Reserved for whatever carries the argument, and
                      used sparingly enough that its presence is itself information.
  Green is absent by design: keeping it as a third colour would reintroduce the
  failing green/orange pair the moment two series shared a view.

  SEMANTICS (rewritten 2026-08-01). Each hue does exactly ONE job:
      grey   #8c8c89  CONTEXT  - on screen, but not what you selected
      blue   #2a78d6  the SUBJECT - what you selected, in a normal state
      orange #eb6834  a CONDITION that wants action. Nothing else.

  The test: "would the user do something differently because this mark is orange?"
  If no, it is not orange. Two prohibitions follow:
      1. orange never marks "the most recent" or "the median"
      2. orange never marks a CATEGORY - only a condition. UTI is not orange for
         being UTI.

  Why this was rewritten rather than clarified: orange had been doing both jobs at
  once - "needs attention" AND "this is ICU". So ICU at 40% was still orange,
  shouting alarm with nothing wrong; and since ICU is always on screen, orange was
  always on screen and had no force left when a threshold genuinely broke. That is
  the same defect this file already warned about for blue ("if it were also the
  accent it would be doing two jobs"), committed with the other colour.

  Identity is now carried by selection, position and label; hue carries only state.
  In an ICU focus the ICU series is BLUE and the network is grey; swap the focus and
  they swap. The alarm is a blue line entering an orange band - which only happens
  when it is true.

  Semantic colour is normally discouraged for accessibility, but that warning is
  really about green/red, which is indistinguishable under protanopia. This pair
  measures 24.7 dE, so it may carry meaning - as long as it never carries meaning
  alone. KPI deltas keep their arrow and sign; highlighted marks keep their label.

  Fonts are NOT set here - a .tps file only holds palettes. The type family is
  Roboto, set at Format -> Workbook, with an Arial fallback. Roboto ships with
  neither Windows nor Tableau and is not embedded in the workbook, so it must be
  installed on whatever machine renders the view. See section 3 of
  docs/v2/design_system.md.
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
