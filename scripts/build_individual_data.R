#!/usr/bin/env Rscript
# Build src/fcompdata/data/individual_data.json from R sources.
#
# Sources:
#   - AirPassengers, BJsales, BJsales.lead, Seatbelts: R `datasets` package
#   - taylor:                                         R `forecast` package
#
# Output schema (per series):
#   sn, h, period, type, description, x, xx
#   xreg (optional): { names: [...], values: [[...], ...] }   row-major, length n + h

suppressMessages({
  library(jsonlite)
  library(forecast)  # for taylor
})

# ---- helpers ----------------------------------------------------------------

split_xreg <- function(mat, h) {
  # mat: matrix with named columns, total rows = n + h
  list(
    names  = as.character(colnames(mat)),
    values = unname(as.matrix(mat))  # row-major when serialised
  )
}

build_entry <- function(sn, series, h, period, type, description, xreg = NULL) {
  v  <- as.numeric(series)
  n  <- length(v) - h
  stopifnot(n > 0)

  entry <- list(
    sn          = sn,
    h           = h,
    period      = period,
    type        = type,
    description = description,
    x           = v[seq_len(n)],
    xx          = v[(n + 1):length(v)]
  )

  if (!is.null(xreg)) {
    stopifnot(nrow(xreg) == length(v))
    entry$xreg <- split_xreg(xreg, h)
  }

  entry
}

# ---- AirPassengers ----------------------------------------------------------

ap <- build_entry(
  sn          = "AirPassengers",
  series      = AirPassengers,
  h           = 12,
  period      = "MONTHLY",
  type        = "monthly",
  description = paste(
    "Monthly totals of international airline passengers (in thousands),",
    "January 1949 to December 1960. Box, G. E. P., Jenkins, G. M.,",
    "Reinsel, G. C. & Ljung, G. M. (2015) Time Series Analysis,",
    "Forecasting and Control. 5th Edition. Wiley. Series G."
  )
)

# ---- BJsales (with BJsales.lead as xreg) ------------------------------------

stopifnot(length(BJsales) == length(BJsales.lead))
bj_xreg <- matrix(as.numeric(BJsales.lead), ncol = 1,
                  dimnames = list(NULL, "BJsales.lead"))

bj <- build_entry(
  sn          = "BJsales",
  series      = BJsales,
  h           = 12,
  period      = "MONTHLY",       # user direction: treat as monthly (R has freq=1)
  type        = "monthly",
  description = paste(
    "Sales data with leading indicator. The variable BJsales is a univariate",
    "time series of length 150; BJsales.lead is its leading indicator,",
    "provided here as a single-column xreg. Box, G. E. P. & Jenkins, G. M.",
    "(1976) Time Series Analysis, Forecasting and Control. Holden-Day.",
    "Series M. Note: R stores both with frequency=1; fcompdata sets",
    "period=12 and type='monthly' by package convention."
  ),
  xreg = bj_xreg
)

# ---- Seatbelts (drivers as response; kms, PetrolPrice, law as xreg) ---------

sb_full <- as.matrix(Seatbelts)
sb_xreg <- sb_full[, c("kms", "PetrolPrice", "law"), drop = FALSE]

sb <- build_entry(
  sn          = "Seatbelts",
  series      = Seatbelts[, "drivers"],
  h           = 12,
  period      = "MONTHLY",
  type        = "monthly",
  description = paste(
    "Road casualties in Great Britain 1969-84. The response variable",
    "(`drivers` column from R's Seatbelts ts) is the monthly total of car",
    "drivers killed or seriously injured. The xreg matrix carries kms",
    "(distance driven), PetrolPrice (real price of petrol), and law (0/1",
    "indicator for compulsory seat-belt legislation, in force from",
    "1983-01-31). Harvey, A. C. & Durbin, J. (1986) The effects of seat",
    "belt legislation on British road casualties: A case study in",
    "structural time series modelling. Journal of the Royal Statistical",
    "Society A, 149, 187-227."
  ),
  xreg = sb_xreg
)

# ---- taylor (half-hourly electricity demand) --------------------------------

ty <- build_entry(
  sn          = "taylor",
  series      = taylor,
  h           = 336,
  period      = "HALFHOURLY",
  type        = "halfhourly",
  description = paste(
    "Half-hourly electricity demand (MW) in England and Wales from",
    "Monday 5 June 2000 to Sunday 27 August 2000 (12 weeks, 4032",
    "observations). Two seasonal cycles: 48 (daily) and 336 (weekly).",
    "Taylor, J. W. (2003) Short-term electricity demand forecasting using",
    "double seasonal exponential smoothing. Journal of the Operational",
    "Research Society, 54, 799-805."
  )
)

# ---- PromoData (CMAF Demand Forecasting workshop, weekly) ------------------

promo_path <- file.path("scripts", "PromoData.csv")
promo <- read.csv(promo_path, stringsAsFactors = FALSE)
stopifnot(nrow(promo) == 156,
          identical(colnames(promo), c("y", "Promo1", "Promo2", "Price")))

# Drop the Price column; only Promo1 and Promo2 are kept as regressors.
promo_xreg <- as.matrix(promo[, c("Promo1", "Promo2")])

pd <- build_entry(
  sn          = "PromoData",
  series      = promo$y,
  h           = 13,
  period      = 52L,        # numeric: weekly with annual seasonality
  type        = "weekly",
  description = paste(
    "Weekly promotional sales data (156 weeks): y is unit sales; Promo1 and",
    "Promo2 are 0/1 indicators for two promotional campaigns. Used in the",
    "CMAF Demand Forecasting course (Session 6.2 - ETS with regressors).",
    "Svetunkov, I. (2024) Demand Forecasting course materials. Centre for",
    "Marketing Analytics and Forecasting (CMAF), Lancaster University",
    "Management School."
  ),
  xreg = promo_xreg
)

# ---- assemble & write -------------------------------------------------------

dataset <- list(
  AirPassengers = ap,
  BJsales       = bj,
  Seatbelts     = sb,
  taylor        = ty,
  PromoData     = pd
)

out_path <- file.path("src", "fcompdata", "data", "individual_data.json")
dir.create(dirname(out_path), recursive = TRUE, showWarnings = FALSE)

writeLines(
  jsonlite::toJSON(
    dataset,
    auto_unbox = FALSE,
    pretty     = FALSE,
    digits     = NA,
    matrix     = "rowmajor"
  ),
  con = out_path
)

cat("Wrote", out_path, "\n")
cat("  AirPassengers : n=", length(ap$x), " h=", ap$h, "\n", sep = "")
cat("  BJsales       : n=", length(bj$x), " h=", bj$h,
    " xreg=", length(bj$xreg$names), "col(s)\n", sep = "")
cat("  Seatbelts     : n=", length(sb$x), " h=", sb$h,
    " xreg=", length(sb$xreg$names), "col(s)\n", sep = "")
cat("  taylor        : n=", length(ty$x), " h=", ty$h, "\n", sep = "")
cat("  PromoData     : n=", length(pd$x), " h=", pd$h,
    " xreg=", length(pd$xreg$names), "col(s)\n", sep = "")
