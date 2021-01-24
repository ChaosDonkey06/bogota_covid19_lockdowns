library(EpiNow2)
library(dplyr)


data_path    = '/Users/chaosdonkey06/Dropbox/bogota_rotating_lockdowns/data/cases/cases_prepared.csv'
r_df_bogota  = read.csv(data_path)

r_df_bogota  = r_df_bogota.c

bogota_rt = epinow2.epinow(reported_cases = r_df_bogota,
                    generation_time = generation_time,
                    delays = epinow2.delay_opts(incubation_period, reporting_delay),
                    rt = epinow2.rt_opts(prior = ro.r.list(mean = 2, sd = 0.2)),
                    stan = epinow2.stan_opts(cores = 4))