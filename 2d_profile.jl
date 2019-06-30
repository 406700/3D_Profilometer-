using Plots
using DelimitedFiles
using Dates

function plot_2d(filename)
    A = readdlm(pwd()*filename, ',', skipstart=5)
    show(A)
    x = A[:,1:1]
    y = A[:,2:2]

    plotly()
    a = plot((x,y))
    plot!(a, xlabel="micrometer", ylabel="nanometer")
end

plot_2d("/3D_data/20190524/man_440_above_step.csv")
plot_2d("/3D_data/20190524/man_440_next_to_step.csv")
