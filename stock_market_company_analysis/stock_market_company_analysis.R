#Rozdział pierwszy 
# Wczytanie danych i konwersja kolumny 'Data' na format daty
data <- read.csv("~/Desktop/Projekt/zwc_d.csv")
data$Data <- as.Date(data$Data, format = "%Y-%m-%d")

# Obliczenie logarytmicznych zwrotów na podstawie kolumny 'Zamkniecie'
data$Log_Zwroty <- c(NA, diff(log(data$Zamkniecie)))
data <- data[!is.na(data$Log_Zwroty), ]

# 1. Wykres cen zamknięcia w czasie
plot(data$Data, data$Zamkniecie, type = "l", col = "blue",
     main = "Dzienny kurs zamknięcia w czasie",
     xlab = "Data", ylab = "Kurs zamknięcia")

# 2. Wykres logarytmicznych zwrotów w czasie
plot(data$Data, data$Log_Zwroty, type = "l", col = "orange",
     main = "Dzienny logarytmiczny zwrot w czasie",
     xlab = "Data", ylab = "Logarytmiczny zwrot")

# Statystyki logarytmicznych zwrotów
srednia_log_zwrot <- mean(data$Log_Zwroty)
wariancja_log_zwrot <- var(data$Log_Zwroty)
odch_std_log_zwrot <- sd(data$Log_Zwroty)
kwantyle <- quantile(data$Log_Zwroty, probs = c(0.05, 0.5, 0.95))

cat("Średni logarytmiczny zwrot:", srednia_log_zwrot, "\n",
    "Wariancja:", wariancja_log_zwrot, "\n",
    "Odchylenie standardowe:", odch_std_log_zwrot, "\n",
    "Kwantyl 5%:", kwantyle[1], "\n",
    "Mediana (50%):", kwantyle[2], "\n",
    "Kwantyl 95%:", kwantyle[3], "\n")

# 3. Histogram logarytmicznych zwrotów z oznaczeniem statystyk
hist(data$Log_Zwroty, breaks = 30, col = "lightblue", main = "Histogram logarytmicznych zwrotów z kwantylami",
     xlab = "Logarytmiczny zwrot", ylab = "Częstość")
abline(v = srednia_log_zwrot, col = "red", lty = 2)       # Średnia
abline(v = kwantyle, col = c("blue", "green", "purple"), lty = 2)

# 4. Wykres dystrybuanty empirycznej
dystrybuanta_empiryczna <- ecdf(data$Log_Zwroty)

# Wygenerowanie punktów do wykresu
x_wartosci <- seq(min(data$Log_Zwroty), max(data$Log_Zwroty), length.out = 100)
y_wartosci <- dystrybuanta_empiryczna(x_wartosci)

# Wykres dystrybuanty empirycznej
plot(x_wartosci, y_wartosci, type = "l", col = "blue",
     main = "Dystrybuanta log-zwrotów",
     xlab = "Logarytmiczny zwrot", ylab = "Dystrybuanta empiryczna (F(x))")

# Dopasowanie rozkładów normalnego i t-Studenta
library(fitdistrplus)
log_returns <- data$Log_Zwroty
fit_norm <- fitdist(log_returns, "norm")
fit_t <- fitdist(log_returns, "t", start = list(df = 380.67))

cat("Parametry rozkładu normalnego:\n",
    "Średnia:", fit_norm$estimate["mean"], "\n",
    "Odchylenie standardowe:", fit_norm$estimate["sd"], "\n")

cat("\nParametry rozkładu t-Studenta:\n",
    "df (liczba stopni swobody):", fit_t$estimate["df"], "\n")

# Wykresy diagnostyczne
par(mfrow = c(2, 2))
hist(log_returns, prob = TRUE, main = "Histogram i dopasowania", col = "lightgray", border = "white", xlab = "Logarytmiczne zwroty")
curve(dnorm(x, mean = fit_norm$estimate["mean"], sd = fit_norm$estimate["sd"]), col = "blue", lwd = 2, add = TRUE)
curve(dt((x - mean(log_returns)) / sd(log_returns), df = fit_t$estimate["df"]) * sd(log_returns) + mean(log_returns), 
      col = "red", lwd = 2, add = TRUE)
legend("topright", legend = c("Rozkład normalny", "Rozkład t-Studenta"), col = c("blue", "red"), lwd = 2, bty = "n")

qqcomp(list(fit_norm, fit_t), legendtext = c("Rozkład normalny", "Rozkład t-Studenta"), main = "Wykres Q-Q")
cdfcomp(list(fit_norm, fit_t), legendtext = c("Rozkład normalny", "Rozkład t-Studenta"), main = "Wykres CDF")
ppcomp(list(fit_norm, fit_t), legendtext = c("Rozkład normalny", "Rozkład t-Studenta"), main = "Wykres P-P")

# Ocena dopasowania - statystyki KS, CM, AD, AIC, BIC
gof_results <- gofstat(list(fn, ft), fitnames = c("normal", "t"))
print(gof_results)

# Test KS z Monte Carlo
set.seed(123)
data <- rnorm(100, mean = 5, sd = 2)
ks_stat <- ks.test(data, "pnorm", mean = mean(data), sd = sd(data))$statistic
n_simulations <- 1000
ks_stats_sim <- numeric(n_simulations)

for (i in 1:n_simulations) {
  simulated_data <- rnorm(100, mean = mean(data), sd = sd(data))
  ks_stats_sim[i] <- ks.test(simulated_data, "pnorm", mean = mean(data), sd = sd(data))$statistic
}

p_value <- mean(ks_stats_sim >= ks_stat)
cat("Statystyka KS dla danych rzeczywistych:", ks_stat, "\n")
cat("P-wartość testu Monte Carlo:", p_value, "\n")

# Rozdział drugi
nike <- read.csv("C://Users/Downloads/nke_us_m.csv")
head(nike)
nike$Date <- as.Date(nike$Data, format="%Y-%m-%d")
nike$LogReturn <- c(NA, diff(log(nike$Zamkniecie)))

#ZADANIE1
if (!require(ggplot2)) install.packages("ggplot2")
library(ggplot2)

#Wykes kursów zamknięcia Akcji Nike
ggplot(nike_clean, aes(x = Date, y = Zamkniecie)) +
  geom_line(color = "blue") +
  labs(title = "Wykres kursu zamknięcia akcji Nike", x = "Data", y = "Kurs zamknięcia") +
  theme_minimal()

#Wykres log-zwrotów Akcji Nike
ggplot(nike_clean, aes(x = Date, y = LogReturn)) +
  geom_line(color = "red") +
  labs(title = "Wykres log-zwrotów akcji Nike", x = "Data", y = "Log-zwrot") +
  theme_minimal()

summary(nike_clean$LogReturn)

#ZADANIE2
mu_hat <- mean(nike$LogReturn, na.rm = TRUE)
sigma2_hat <- var(nike$LogReturn, na.rm = TRUE)

# Zakladajac, ze kolumna 'LogReturn' zawiera dane log-zwrot?w
log_returns <- nike$LogReturn

# 1. Estymacja wartosci oczekiwanej (srednia)
mean_log_return <- mean(log_returns, na.rm = TRUE)
cat("Estymowana wartosc oczekiwana: ", mean_log_return, "\n")

# 2. Estymacja wariancji
variance_log_return <- var(log_returns, na.rm = TRUE)
cat("Estymowana wariancja: ", variance_log_return, "\n")

# 3. Estymacja odchylenia standardowego
sd_log_return <- sd(log_returns, na.rm = TRUE)
cat("Estymowane odchylenie standardowe: ", sd_log_return, "\n")

# 4. Estymacja kwantyli (a = 5%, 50%, 95%)
quantiles <- quantile(log_returns, probs = c(0.05, 0.50, 0.95), na.rm = TRUE)

cat("Kwantyle 5%, 50%, 95%: \n", quantiles, "\n")

# Zaladuj niezbedne pakiety
library(ggplot2)
library(gridExtra)

# 1. Obliczanie wartości oczekiwanej (średnia)
mean_log_return <- mean(log_returns, na.rm = TRUE)

# 2. Obliczanie wariancji
variance_log_return <- var(log_returns, na.rm = TRUE)

# 3. Obliczanie odchylenia standardowego
sd_log_return <- sd(log_returns, na.rm = TRUE)

# 4. Obliczanie kwantyli (5%, 50%, 95%)
quantiles <- quantile(log_returns, probs = c(0.05, 0.50, 0.95), na.rm = TRUE)

# 2. Tworzenie tabeli z wynikami
results <- data.frame(
  Metric = c("Wartosc oczekiwana", "Wariancja", "Odchylenie standardowe", 
             "Kwantyl 5%", "Kwantyl 50%", "Kwantyl 95%"),
  Value = c(mean_log_return, variance_log_return, sd_log_return,
            quantiles[1], quantiles[2], quantiles[3])
)

# 3. Tworzenie wykresu tabeli
table_plot <- ggplot(results, aes(x = Metric, y = Value)) +
  geom_text(aes(label = round(Value, 4)), size = 5, hjust = 0.5, vjust = 0.5) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        axis.title = element_blank(),
        axis.text.y = element_blank(),
        axis.ticks = element_blank(),
        panel.grid = element_blank())

install.packages("fitdistrplus")

library(ggplot2)

library(fitdistrplus)

# Dopasowanie rozkladów
mean_value <- mean(nike$LogReturn, na.rm = TRUE)
sd_value <- sd(nike$LogReturn, na.rm = TRUE)
df_value <- 5

fit_normal <- fitdist(nike$Zamkniecie, "norm")
fit_t_student <- fitdist(nike$Zamkniecie, "t", start = list(df = df_value, mean = mean_value, sd = sd_value))
# Wykresy diagnostyczne dla rozkladu normalnego
par(mfrow=c(2,2))  # Uklad wykresów: 2x2
plot(fit_normal)

# Wykresy diagnostyczne dla rozkladu t-Studenta
plot(fit_t_student)



if (!require(gridExtra)) install.packages("gridExtra")
if (!require(png)) install.packages("png")

library(gridExtra)
library(png)

nike <- read.csv("C:\\Users\\jaczk\\Downloads\\nke_us_m.csv")
nike$LogReturn <- c(NA, diff(log(nike$Zamkniecie)))
#Tabela z wyestymowanymi kwantylami
sample_mean <- mean(nike$LogReturn, na.rm = TRUE)
variance <- var(nike$LogReturn, na.rm = TRUE)
std_deviation <- sqrt(variance)
quantiles <- quantile(nike$LogReturn, probs = c(0.05, 0.5, 0.95), na.rm = TRUE)

results <- data.frame(
  sample_mean, 
  variance, 
  std_deviation,
  quantiles[1],
  quantiles[2],
  quantiles[3]
)

colnames(results) <- c(
  "x̄ₙ",
  "s²n",
  "sn",
  "q(5%)",
  "q(50%)",
  "q(95%)"
)

png(filename = "kwantyle.png", width = 800, height = 100)
grid.table(results)

dev.off()
# Histogram log-zwrotów
ggplot(nike, aes(x = LogReturn)) +
  geom_histogram(binwidth = 0.005, fill = "skyblue", color = "black", alpha = 0.7) +
  geom_vline(aes(xintercept = sample_mean), color = "blue", linetype = "dashed", size = 1) +
  geom_vline(aes(xintercept = quantiles[1]), color = "red", linetype = "dashed", size = 1) +
  geom_vline(aes(xintercept = quantiles[2]), color = "green", linetype = "dashed", size = 1) +
  geom_vline(aes(xintercept = quantiles[3]), color = "purple", linetype = "dashed", size = 1) +
  labs(title = "Histogram Log-Zwrotów",
       x = "Log-Zwrot", y = "Gęstość") +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_x_continuous(limits = c(-0.1, 0.15)) +  
  scale_y_continuous(limits = c(0, 15))          

x_values <- seq(min(nike$LogReturn, na.rm = TRUE), max(nike$LogReturn, na.rm = TRUE), length.out = 100)
F_n_values <- sapply(x_values, function(x) sum(nike$LogReturn <= x, na.rm = TRUE) / (length(nike$LogReturn) - 1))

ggplot(data.frame(x = x_values, F_n = F_n_values), aes(x = x, y = F_n)) +
  geom_line(color = "blue", size = 1) +
  labs(title = "Empiryczna Funkcja Rozkładu Log-Zwrotów Akcji Nike", x = "Log-Zwrot", y = "F_n(x)") +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5))

#ZADANIE3
nike <- read.csv("C://Users/jaczk/Downloads/nke_us_m.csv")
head(kursy_zamk)  # Wyświetli pierwsze kilka wartości
summary(kursy_zamk)  # Podsumowanie zmiennej, w tym wartości min, max, NA


# kursy zamkniecia/dzienne log-zwroty (stopy zwrotu)
kursy_zamk <- nike$Zamkniecie
R <- diff(log(kursy_zamk))


# 1 S=(s1, s2, ..., Sn)

# 2 log(S2/S1)=logS2 - logS1
# logS = log(s) = (logS1, logS2,...,logSn)
# 3 R = diff(logs) = diff(log(s)) = (logS2 - logS1, logS3-logS2, .., logSn-logSn-1) = (logS2/ s1, log s3/s2)

#wykresy kursow i log-zwrotow
m1 <- mean(kursy_zamk); m1
m2 <- mean(R); m2

par(mfrow=c(2,2))
hist(kursy_zamk, prob=TRUE)
plot(kursy_zamk)
abline(h=m1,col=2,lwd=2)
grid()

#kwantyl 5%
Q5 <- quantile(R, 0.05); Q5

#kwantyl 50% mediana
Q50 <- quantile(R, 0.5); Q50

#kwantyl 95%
Q95 <- quantile(R, 0.95); Q95

Qs <- c(Q5, Q50, Q95)


#hist(R, prob=TRUE)
#plot(R)
#abline(h=m1,col=2,lwd=2)
#grid()

gofstat(list(fn, ft),  fitnames = c("normal", "t"))

hist(R, prob=TRUE)
#Dodanie do histogramu
points(m2, 0, col=4, pch=19)
points((Qs), c(0,0,0), col=3, pch=19)
plot(R)
abline(h=m2,col=2,lwd=2)
grid()

var_nob <- var(R); var_nob

od_st <- sqrt(var_nob); od_st

library(fitdistrplus)

hist(R,prob=TRUE)

fn <- fitdistrplus::fitdist(R, "norm")
ft <- fitdistrplus::fitdist(R, "t", start=list(df=12))

#par(mfrow=c(1,1))
#curve(dnorm(x,fn$estimate[1],fn$estimate[2]), xlim=c(-4,4),lwd=2)
#curve(dt(x,ft$estimate), add=T, col=2,lwd=2)

#WYKRESY DIAGNOSTYCZNE

par(mfrow=c(2,2))

plot.legend <- c("normal", "t")
denscomp(list(fn, ft), legendtext = plot.legend)
qqcomp(list(fn, ft), legendtext = plot.legend)
cdfcomp(list(fn, ft), legendtext = plot.legend)
ppcomp(list(fn, ft), legendtext = plot.legend)

ft$estimate
#wyestymowane 314

#dystrybuanta
v <- 300
curve(dt(x,v), xlim=c(-3,3))

gofstat(list(fn, ft),  fitnames = c("normal", "t"))
#curve(dt(x,10), xlim=c(-3,3), col='blue', add=T, lxd=2)

#1. Rozklad statystyki Dn (metoda MC).
#Generujemy N=10000 probek licznosci n=100 z rozkladu F0=Exp(0.98) wybranego w Przykladzie 3 
#i obliczamy odleglosc dystrybuant empirycznych od rozkladu F0 (wartosc statystyki Dn).
N <- 10000
n <- length(R); n

D <- c()

for (i in 1:N) { 
  
  Y <- rnorm(n, fn$estimate[1],fn$estimate[2]) 
  D[i] <- ks.test(Y,pnorm,fn$estimate[1],fn$estimate[2],exact=TRUE)$statistic
}

#2. Obliczamy dn wartosc statystyki dla proby X i F0.
dn <- ks.test(R,pnorm,fn$estimate[1],fn$estimate[2],exact=TRUE)$statistic

#wyniki na histogramie
hist(D,prob=T, main="rozklad statystyki", xlab = "statystyka Dn", ylab = "gestosc")
points(dn,0,pch=19,col=2)

#3. Obliczamy p-value
p_value <- length(D[D>dn])/N; p_value

#Przyjmujemy poziom istotnosci 5%
alpha <- 0.05
p_value <= alpha

if (p_value <= alpha){
  cat("\nNa poziomie istotnosci", alpha, "odrzucamy hipoteze H0.\n")
} else {
  cat("\nNa poziomie istotnosci", alpha, "nie ma podstaw do odrzucenia hipoteze H0.\n")
}

# Rozdział trzeci - wspólny 

# Wczytanie danych i konwersja kolumny 'Data' na format daty
data <- read.csv("~/Desktop/Projekt/zwc_d.csv")
data$Data <- as.Date(data$Data, format = "%Y-%m-%d")

# Obliczenie logarytmicznych zwrotów na podstawie kolumny 'Zamkniecie'
data$Log_Zwroty <- c(NA, diff(log(data$Zamkniecie)))
data <- data[!is.na(data$Log_Zwroty), ]
# Wczytanie danych i konwersja kolumny 'Data' na format daty
data1 <- read.csv("~/Desktop/Projekt/Projekt/nke_us_m.csv")
data1$Data <- as.Date(data1$Data, format = "%Y-%m-%d")

# Obliczenie logarytmicznych zwrotów na podstawie kolumny 'Zamkniecie'
data1$Log_Zwroty <- c(NA, diff(log(data1$Zamkniecie)))
data1 <- data1[!is.na(data1$Log_Zwroty), ]

data_combined <- merge(data[, c("Data", "Log_Zwroty")], 
                       data1[, c("Data", "Log_Zwroty")], 
                       by = "Data", suffixes = c("_Spolka1", "_Spolka2"))

head(data_combined)

# Estymacja parametrów
mu <- colMeans(data_combined[, c("Log_Zwroty_Spolka1", "Log_Zwroty_Spolka2")])
Sigma <- cov(data_combined[, c("Log_Zwroty_Spolka1", "Log_Zwroty_Spolka2")])
P <- cor(data_combined[, c("Log_Zwroty_Spolka1", "Log_Zwroty_Spolka2")])
rho <- cor(data_combined$Log_Zwroty_Spolka1, data_combined$Log_Zwroty_Spolka2)

# Wyświetlenie wyników
print("Wektor średnich:")
print(mu)
print("Macierz kowariancji:")
print(Sigma)
print("Macierz korelacji:")
print(P)
print("Współczynnik korelacji:")
print(rho)

# Załaduj pakiety
library(ggplot2)
library(ggExtra)

# Tworzenie wykresu rozrzutu
scatter_plot <- ggplot(data_combined, aes(x = Log_Zwroty_Spolka1, y = Log_Zwroty_Spolka2)) +
  geom_point(alpha = 0.7, color = "blue") + # Punkty
  labs(x = "Log-zwroty Spółka 1",
       y = "Log-zwroty Spółka 2") +
  theme_minimal()

# Dodanie histogramów brzegowych
scatter_with_marginals <- ggMarginal(scatter_plot, type = "histogram", bins = 30, fill = "lightblue")

# Wyświetlenie wykresu
print(scatter_with_marginals)

library(mvtnorm)
library(ggplot2)

# Parametry wyestymowane wcześniej
mu <- colMeans(data_combined[, c("Log_Zwroty_Spolka1", "Log_Zwroty_Spolka2")])
Sigma <- cov(data_combined[, c("Log_Zwroty_Spolka1", "Log_Zwroty_Spolka2")])

# Siatka punktów do rysowania gęstości
x <- seq(min(data_combined$Log_Zwroty_Spolka1), max(data_combined$Log_Zwroty_Spolka1), length.out = 100)
y <- seq(min(data_combined$Log_Zwroty_Spolka2), max(data_combined$Log_Zwroty_Spolka2), length.out = 100)
grid <- expand.grid(x = x, y = y)

# Obliczenie gęstości łącznej
grid$z <- dmvnorm(cbind(grid$x, grid$y), mean = mu, sigma = Sigma)

# Wykres gęstości łącznej
ggplot(grid, aes(x = x, y = y, z = z)) +
  geom_contour_filled() +
  labs(x = "Log-zwroty Spółka 1",
       y = "Log-zwroty Spółka 2") +
  theme_minimal()

# Ustawienie układu dwóch wykresów obok siebie
par(mfrow = c(1, 2))

# Gęstość brzegowa dla Spółki 1
x <- seq(min(data_combined$Log_Zwroty_Spolka1), max(data_combined$Log_Zwroty_Spolka1), length.out = 100)
x_density <- dnorm(x, mean = mu[1], sd = sqrt(Sigma[1, 1]))
plot(x, x_density, type = "l", col = "blue", lwd = 2,
     main = "Gęstość brzegowa Spółki 1",
     xlab = "Log-zwroty Spółka 1", ylab = "Gęstość")

# Gęstość brzegowa dla Spółki 2
y <- seq(min(data_combined$Log_Zwroty_Spolka2), max(data_combined$Log_Zwroty_Spolka2), length.out = 100)
y_density <- dnorm(y, mean = mu[2], sd = sqrt(Sigma[2, 2]))
plot(y, y_density, type = "l", col = "green", lwd = 2,
     main = "Gęstość brzegowa Spółki 2",
     xlab = "Log-zwroty Spółka 2", ylab = "Gęstość")

# Przywrócenie domyślnego układu
par(mfrow = c(1, 1))

# Załaduj pakiety
library(MASS)  # Do generowania danych z rozkładu wielowymiarowego

# Estymacja parametrów
mu <- colMeans(data_combined[, c("Log_Zwroty_Spolka1", "Log_Zwroty_Spolka2")])
Sigma <- cov(data_combined[, c("Log_Zwroty_Spolka1", "Log_Zwroty_Spolka2")])

# Generowanie nowej próby z rozkładu N(mu, Sigma)
simulated_data <- mvrnorm(n = nrow(data_combined), mu, Sigma)
simulated_df <- data.frame(Log_Zwroty_Spolka1 = simulated_data[, 1],
                           Log_Zwroty_Spolka2 = simulated_data[, 2])

# Porównanie wykresów rozrzutu dla danych rzeczywistych i symulowanych
# Ustawienie układu na dwa wykresy obok siebie
par(mfrow = c(1, 2))

# Wykres danych rzeczywistych
plot(data_combined$Log_Zwroty_Spolka1, data_combined$Log_Zwroty_Spolka2,
     col = "blue", pch = 16, main = "Dane rzeczywiste",
     xlab = "Log-Zwroty Spółka 1", ylab = "Log-Zwroty Spółka 2")

# Wykres danych symulowanych
plot(simulated_df$Log_Zwroty_Spolka1, simulated_df$Log_Zwroty_Spolka2,
     col = "red", pch = 16, main = "Dane symulowane",
     xlab = "Log-Zwroty Spółka 1", ylab = "Log-Zwroty Spółka 2")

# Przywrócenie domyślnego układu wykresów
par(mfrow = c(1, 1))

#3.1
# Obliczenie statystyk dla obu spółek
mean_spolka1 <- mean(data_combined$Log_Zwroty_Spolka1, na.rm = TRUE)
mean_spolka2 <- mean(data_combined$Log_Zwroty_Spolka2, na.rm = TRUE)

sd_spolka1 <- sd(data_combined$Log_Zwroty_Spolka1, na.rm = TRUE)
sd_spolka2 <- sd(data_combined$Log_Zwroty_Spolka2, na.rm = TRUE)

n_spolka1 <- sum(!is.na(data_combined$Log_Zwroty_Spolka1))
n_spolka2 <- sum(!is.na(data_combined$Log_Zwroty_Spolka2))

cat("Spółka 1: Średnia =", mean_spolka1, ", Odchylenie standardowe =", sd_spolka1, ", n =", n_spolka1, "\n")
cat("Spółka 2: Średnia =", mean_spolka2, ", Odchylenie standardowe =", sd_spolka2, ", n =", n_spolka2, "\n")

# Poziom ufności
alpha <- 0.05

# Kwantyle t-Studenta
t_spolka1 <- qt(1 - alpha / 2, df = n_spolka1 - 1)
t_spolka2 <- qt(1 - alpha / 2, df = n_spolka2 - 1)

# Przedziały ufności
ci_spolka1 <- c(
  mean_spolka1 - t_spolka1 * sd_spolka1 / sqrt(n_spolka1),
  mean_spolka1 + t_spolka1 * sd_spolka1 / sqrt(n_spolka1)
)

ci_spolka2 <- c(
  mean_spolka2 - t_spolka2 * sd_spolka2 / sqrt(n_spolka2),
  mean_spolka2 + t_spolka2 * sd_spolka2 / sqrt(n_spolka2)
)

cat("Przedział ufności dla średniej log-zwrotów Spółki 1:", ci_spolka1, "\n")
cat("Przedział ufności dla średniej log-zwrotów Spółki 2:", ci_spolka2, "\n")

# 3.2

# Ustawienie układu wykresów
par(mfrow = c(2, 2))

# Model regresji liniowej 
lm_model <- lm(Log_Zwroty_Spolka2 ~ Log_Zwroty_Spolka1, data = data_combined)
summary(lm_model)

# Wykres rozrzutu z linią regresji
library(ggplot2)
ggplot(data_combined, aes(x = Log_Zwroty_Spolka1, y = Log_Zwroty_Spolka2)) +
  geom_point(color = "blue") +
  geom_smooth(method = "lm", se = FALSE, color = "red") +
  labs(title = "Regresja liniowa dla log-zwrotów", x = "Log-Zwroty Spółka 1", y = "Log-Zwroty Spółka 2") +
  theme_minimal()

# Analiza reszt
residuals <- lm_model$residuals

# Histogram reszt
hist(residuals, breaks = 20, col = "lightblue", main = "Histogram reszt", xlab = "Reszty")

# QQ-plot reszt
qqnorm(residuals)
qqline(residuals, col = "red")

# Testy normalności reszt
library(nortest)
shapiro_test <- shapiro.test(residuals)
ad_test <- ad.test(residuals)

cat("Shapiro-Wilk Test p-value:", shapiro_test$p.value, "\n")
cat("Anderson-Darling Test p-value:", ad_test$p.value, "\n")

# Istotność współczynników
summary(lm_model)

# Współczynnik determinacji 
cat("Współczynnik determinacji R^2:", summary(lm_model)$r.squared, "\n")

# Predykcja
mean_R1 <- mean(data_combined$Log_Zwroty_Spolka1, na.rm = TRUE)
predicted_R2 <- predict(lm_model, newdata = data.frame(Log_Zwroty_Spolka1 = mean_R1))

cat("Przewidywane R2 dla średniego R1:", predicted_R2, "\n")

# Uproszczony model, jeśli b0 jest nieistotny
if (summary(lm_model)$coefficients[1, 4] > 0.05) {
  lm_model_simple <- lm(Log_Zwroty_Spolka2 ~ Log_Zwroty_Spolka1 - 1, data = data_combined)
  predicted_R2_simple <- predict(lm_model_simple, newdata = data.frame(Log_Zwroty_Spolka1 = mean_R1))
  cat("Przewidywane R2 dla uproszczonego modelu:", predicted_R2_simple, "\n")
}

# Przedziały ufności dla predykcji 
conf_int <- predict(lm_model, newdata = data.frame(Log_Zwroty_Spolka1 = mean_R1), interval = "confidence")
cat("Analityczny przedział ufności dla predykcji:", conf_int, "\n")

# Metoda bootstrap dla przedziałów ufności
set.seed(123)
B <- 1000
bootstrap_preds <- numeric(B)
for (i in 1:B) {
  sample_indices <- sample(1:nrow(data_combined), replace = TRUE)
  bootstrap_data <- data_combined[sample_indices, ]
  bootstrap_model <- lm(Log_Zwroty_Spolka2 ~ Log_Zwroty_Spolka1, data = bootstrap_data)
  bootstrap_preds[i] <- predict(bootstrap_model, newdata = data.frame(Log_Zwroty_Spolka1 = mean_R1))
}

bootstrap_ci <- quantile(bootstrap_preds, probs = c(0.025, 0.975))
cat("Bootstrapowy przedział ufności dla predykcji:", bootstrap_ci, "\n")

# Histogram bootstrapowych przewidywań
hist(bootstrap_preds, breaks = 30, col = "lightblue", 
     main = "Rozkład bootstrapowych przewidywań",
     xlab = "Przewidywane wartości R2")
abline(v = mean(bootstrap_preds), col = "red", lwd = 2, lty = 2) # Średnia

# Reszty w funkcji przewidywanych wartości
plot(lm_model$fitted.values, residuals, 
     main = "Reszty w funkcji przewidywanych wartości",
     xlab = "Przewidywane wartości", ylab = "Reszty", 
     pch = 19, col = "blue")
abline(h = 0, col = "red", lwd = 2)

par(mfrow = c(1, 1))
# Porównanie wartości rzeczywistych i przewidywanych
plot(data_combined$Log_Zwroty_Spolka2, lm_model$fitted.values,
     main = "Wartości rzeczywiste vs przewidywane",
     xlab = "Rzeczywiste wartości R2", ylab = "Przewidywane wartości R2",
     pch = 19, col = "blue")
abline(0, 1, col = "red", lwd = 2)

