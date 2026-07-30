"""Crosswalk from SIH's bed specialty to CNES's bed type.

The two fact tables classify beds with different, independently maintained code sets:

``aihs_reduzidas.especialidade_leito``
    41 codes, SIH's own. The specialty the *admission* was billed under — one value per
    admission (e.g. ``03-Clínico``, ``75-UTI Adulto II``, ``09-Leito Dia / Cirúrgicos``).

``leito.tipo_leito``
    7 values, CNES's. The type of *bed registered at the hospital* (``clinico``,
    ``cirurgico``, ``obstetricos``, ``pediatricos``, ``complementar``,
    ``outras especialidades``, ``hospital dia``).

An occupancy rate per bed type needs both sides on one vocabulary: bed-days from SIH in
the numerator, registered beds from CNES in the denominator. This module maps the finer
SIH set onto the coarser CNES set, which is the only direction that doesn't invent
detail.

**This is an approximation, and the direction of its error is knowable.** A patient
billed under one specialty may physically occupy a bed registered as another, so a
per-type rate is softer evidence than the network-wide rate. Three specific cautions,
all verified against RS 2019-2023 rather than assumed:

* **ICU cannot come from here at all.** Of the crosswalk's 41 codes, RS uses only 13, and
  not one of them is an ICU code — no 74-83, no 51/52, no 92-96. Intensive care is
  recorded exclusively in the separate ``quantidade_dias_uti_mes`` counter, which is
  independent of ``especialidade_leito``: a patient admitted to a clinical bed who spends
  four days in intensive care keeps ``especialidade_leito = 03`` and reports 4 ICU days.
  Deriving ICU occupancy from the specialty code would therefore return zero, not an
  undercount. Use the day counter — see ``OccupancyCalculator``.
* **ICU days are not a clean subset of stay days**, so ward days cannot be computed as
  ``permanencia - dias_uti``. On 37.483 of 342.929 ICU admissions (11%) the ICU counter
  *exceeds* total stay days, because ``quantidade_dias_uti_mes`` is a per-month figure
  while a long stay is split across several monthly AIHs. Subtracting would produce
  negative ward days on ~1% of all rows. The per-ward-type rate therefore uses stay days
  as-is and slightly overstates ward use, since days a patient spent in ICU still count
  against the ward they were admitted to. Stated rather than silently clamped.
* ``complementar`` is not a synonym for ICU. It bundles true ICU/coronary units with
  intermediate-care units and isolation beds. In 2023 only ~1.839 of RS's 2.404
  ``complementar`` SUS beds are actual ICU/UCO, so labelling the category "UTI"
  overstates intensive care by roughly a third.

One further caveat belongs to the reader of any per-type rate rather than to this module:
``hospital dia`` measures 18,2% in 2023 not because day-hospital beds are idle but because
they turn over within a single day, so a bed-*day* denominator is the wrong unit for them.
"""

# SIH especialidade_leito code -> CNES tipo_leito value.
# Keys are the dictionary's `chave` values, which are strings without zero padding.
SIH_TO_CNES_BED_TYPE: dict[str, str] = {
    # --- direct equivalents -------------------------------------------------
    "1": "cirurgico",      # 01-Cirúrgico
    "2": "obstetricos",    # 02-Obstétricos
    "3": "clinico",        # 03-Clínico
    "7": "pediatricos",    # 07-Pediátricos
    # --- CNES folds these into "outras especialidades" ----------------------
    "4": "outras especialidades",   # 04-Crônicos
    "5": "outras especialidades",   # 05-Psiquiatria
    "6": "outras especialidades",   # 06-Pneumologia Sanitária (Tisiologia)
    "8": "outras especialidades",   # 08-Reabilitação
    "84": "outras especialidades",  # 84-Acolhimento Noturno
    # --- day-hospital variants ---------------------------------------------
    "9": "hospital dia",    # 09-Leito Dia / Cirúrgicos
    "10": "hospital dia",   # 10-Leito Dia / Aids
    "11": "hospital dia",   # 11-Leito Dia / Fibrose Cística
    "12": "hospital dia",   # 12-Leito Dia / Intercorrência Pós-Transplante
    "13": "hospital dia",   # 13-Leito Dia / Geriatria
    "14": "hospital dia",   # 14-Leito Dia / Saúde Mental
    # --- specialty-flavoured clinical and surgical beds ---------------------
    # CNES registers these as clinical/surgical beds with a specialty attribute, so
    # they roll up rather than forming categories of their own.
    "87": "clinico",     # 87-Saúde Mental (Clínico)
    "88": "clinico",     # 88-Queimado Adulto (Clínico)
    "89": "clinico",     # 89-Queimado Pediátrico (Clínico)
    "90": "cirurgico",   # 90-Queimado Adulto (Cirúrgico)
    "91": "cirurgico",   # 91-Queimado Pediátrico (Cirúrgico)
    # --- everything CNES calls "complementar" ------------------------------
    # Intensive care, coronary care, intermediate care and COVID ventilatory support.
    "51": "complementar",  # 51-UTI II Adulto COVID 19
    "52": "complementar",  # 52-UTI II Pediátrica COVID 19
    "64": "complementar",  # 64-Unidade Intermediária
    "65": "complementar",  # 65-Unidade Intermediária Neonatal
    "74": "complementar",  # 74-UTI I
    "75": "complementar",  # 75-UTI Adulto II
    "76": "complementar",  # 76-UTI Adulto III
    "77": "complementar",  # 77-UTI Infantil I
    "78": "complementar",  # 78-UTI Infantil II
    "79": "complementar",  # 79-UTI Infantil III
    "80": "complementar",  # 80-UTI Neonatal I
    "81": "complementar",  # 81-UTI Neonatal II
    "82": "complementar",  # 82-UTI Neonatal III
    "83": "complementar",  # 83-UTI Queimados
    "85": "complementar",  # 85-UTI Coronariana-UCO tipo II
    "86": "complementar",  # 86-UTI Coronariana-UCO tipo III
    "92": "complementar",  # 92-UCI Neonatal (convencional)
    "93": "complementar",  # 93-UCI Neonatal (canguru)
    "94": "complementar",  # 94-UCI Pediátrica
    "95": "complementar",  # 95-UCI Adulto
    "96": "complementar",  # 96-Suporte Ventilatório Pulmonar COVID-19
}

# SIH especialidade_leito codes for COVID-designated beds. Kept for documentation and for
# any future scope beyond RS, but NOT surfaced as a column: verified zero rows across all
# 3.739.506 RS admissions in 2019-2023. RS billed pandemic ICU stays under the ordinary
# ICU day counter instead of these codes.
#
# Emitting a flag that is False on every row would be worse than omitting it — it is a
# filter that appears to work and does nothing, which is the same defect as offering a
# "Macrorregião" filter with no macro-region field behind it.
COVID_BED_CODES: tuple[str, ...] = ("51", "52", "96")

# CNES tipo_especialidade_leito values that are genuinely intensive or coronary care,
# as opposed to the rest of "complementar". Matched case-insensitively by prefix.
#
# Verified against RS 2023: these prefixes select 1.839,0 mean monthly SUS beds and
# exclude 565,3. Everything excluded is an intermediate-care or isolation unit
# ("unidade de cuidados intermediarios adulto/neonatal/pediatrico", "unidade
# isolamento") — no intensive-care bed is left out. Coronary units are caught by
# "uti " because CNES names them "uti coronariana tipo ii - uco tipo ii"; the "uco "
# prefix is kept for other states and years that may name them differently.
ICU_SPECIALTY_PREFIXES: tuple[str, ...] = ("uti ", "uco ")


def sql_case_expression(column: str, default: str = "outras especialidades") -> str:
    """A DuckDB CASE expression mapping a SIH specialty column to a CNES bed type.

    Args:
        column: qualified name of the especialidade_leito column (e.g. ``a.especialidade_leito``).
        default: bed type for codes absent from the crosswalk. Defaults to the same
            catch-all CNES itself uses, so an unmapped new code degrades into the
            residual category instead of becoming NULL and silently dropping rows.
    """
    whens = "\n".join(
        f"                    WHEN '{code}' THEN '{bed_type}'"
        for code, bed_type in SIH_TO_CNES_BED_TYPE.items()
    )
    return (
        f"CASE {column}\n{whens}\n"
        f"                    ELSE '{default}'\n"
        f"                END"
    )


def sql_is_covid_bed(column: str) -> str:
    """A DuckDB boolean expression: was this admission in a COVID-designated bed?"""
    codes = ", ".join(f"'{c}'" for c in COVID_BED_CODES)
    return f"{column} IN ({codes})"


def sql_is_icu_specialty(column: str) -> str:
    """A DuckDB boolean expression selecting true ICU/coronary beds within complementar."""
    tests = " OR ".join(
        f"lower({column}) LIKE '{prefix}%'" for prefix in ICU_SPECIALTY_PREFIXES
    )
    return f"({tests})"
