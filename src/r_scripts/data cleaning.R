rm(list=ls())
setwd("~/GitHub/AMLO-NLP/")
library(tidyverse)
library(stargazer)
library(readxl)
library(lubridate)

# Texto conferencias
conferences_data <- read.csv("conferences_data.csv")

# Sentiment Score
complete_data <- read.csv("src/data/complete_dataset_BDD.csv") # Versión Nnet

# Datos mensuales
table_aprobacion <- read_excel("table-aprobacion.xlsx")
ipc_2018_2024 <- read_excel("ipc 2018-2024.xlsx", 
                            col_types = c("date", "numeric"))

google1 <- read.csv("google1.csv")
google2 <- read.csv("google2.csv")
google3 <- read.csv("google3.csv")
google4 <- read.csv("google4.csv")

# Datos diarios
dolar <- read_csv("precio dolar 2018-2024.csv")
casos_covid <- read_csv("Casos_Diarios_Estado_Nacional_Confirmados_20230625.csv")

# Data Cleaning

dolar <- dolar |>
  rename(dates = fecha) |>
  mutate(as.Date(dates))

complete_data <- complete_data |> 
  mutate(dates = as.Date(dates)) 

# Diario

complete_data <- complete_data |>
  select(!c(nnet_score_x, nnet_score_y)) |>
  rename(homicides_gov = homicidios_fuentes_gobierno,
         homicides_open = homicidios_fuentes_abiertas)

write.csv(complete_data, file = "complete_data_daily.csv", row.names = FALSE)

# Mensual 

complete_data_monthly <- complete_data |>
  mutate(dates = as.Date(dates, format = "%Y-%m-%d %H:%M:%S"),
         year = as.factor(year(dates)), 
         month = month(dates), 
         day = day(dates)) |>
  group_by(month, year) |>
  summarize(median_nnet = median(nnet_score),
            mean_nnet = mean(nnet_score),
            homicides_open = sum(homicides_open),
            homicides_gov = sum(homicides_gov),
            median_words = median(num_words),
            mean_words = mean(num_words))

ipc_2018_2024 <- ipc_2018_2024 |>
  rename(date = Fecha) |>
  mutate(date = as.Date(date, format = "%Y-%m-%d %H:%M:%S"), 
         year = as.factor(year(date)), 
         month = month(date), 
         day = day(date)) |>
  group_by(month, year) |>
  select(!c(day)) 

complete_data_monthly <- complete_data_monthly |>
  mutate(year = as.integer(as.character(year)),
         month = as.integer(month),
         date = make_date(year, month, 1))


table_aprobacion <- table_aprobacion |>
  mutate(year = as.integer(str_extract(Mes, "\\d{4}$")),
    month = match(str_extract(Mes, "^[A-Za-z]+"), month.abb),
    date = make_date(year, month, 1))

table_aprobacion_month <- table_aprobacion |>
  group_by(date) |>
  summarize(approves_mean = mean(Aprueba),
            disapproves_mean = mean(Desaprueba))

google_trends <- google1 |>
  left_join(google2, by = "mes") |>
  left_join(google3, by = "mes") |>
  left_join(google4, by = "mes") |>
  rename(date = mes,
         president_journalist_trend = presidente_periodista_mx,
         violence_journalist_trend1 = violencia_periodista.x,
         violence_journalist_trend2 = violencia_periodista.y) |>
  separate(date, into = c("year", "month"), sep = "-") |>
  mutate(year = as.integer(year),
    month = as.integer(month),
    date = make_date(year, month, 1))


complete_data_monthly <- complete_data_monthly |>
  left_join(ipc_2018_2024, by = "date") |>
  left_join(table_aprobacion_month, by = "date") |>
  left_join(google_trends, by = "date")




write.csv(complete_data_monthly, file = "complete_data_monthly.csv", row.names = FALSE)
