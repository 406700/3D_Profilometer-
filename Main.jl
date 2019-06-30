using Plots
using DelimitedFiles
#using GLM
using DataFrames
using Dates
using PyCall #using conda for own julia environment
#PyCall.conda ==true
pushfirst!(PyVector(pyimport("sys")."path"), "") #add modules from current directory

pyimport("sdfsimple")


function plot_3d()

    A = readdlm()
    x = A[:,1:1] ##amps
    y = A[:,2:2] ##volts

    # x, y, f(x,y)

    Plotly()
    sts = (:contour,:heatmap,:surface,:wireframe)
    a = plot((x,y), st = sts, title=fiber.fiber_id*" : $Rs ohms cm:", label="Measured data")
    plot!(a, xlabel="Amps", ylabel="Volts")
    plot!(a,(vec(A[:,1:1]),z), label="Linear Fit") #plots the line using predicted values
    gui(a) #plots in a separate pane

    #save figure
    date = Dates.format(Dates.now(), "yyyy-mm-dd HH:MM:SS") #current time formatted as string
    directory = pwd()*"/Plots/"*string(fiber.fiber_id)*"/"*fiber.sample*"/"
    mkpath(directory) # creates the full file path if it doesn't exist
    savefile_as = directory*fiber.date*"_"*date*"_"*string(fiber.pad_number)*filename_addition
    savefig(a, savefile_as) #saves figure, automatically detects extension

    #create and save a text file with info

    fname = savefile_as # current directory
    f = open(fname, "w+")
    truncate(f,0)
    print(f, " file_name " * fiber.file_name * "\n fiber_id " * fiber.fiber_id* "\n sample " * fiber.sample * "\n material " * fiber.material * "\n date " * fiber.date * "\n core_diameter " * string(fiber.core_diameter) * "\n polished_diameter " * string(fiber.polished_diameter) * "\n Not polished past mid point " * string(fiber.top_half) * "\n contact_spacing " * string(fiber.contact_spacing) * "\n pad_number " * string(fiber.pad_number) * "\n text_addition")
    close(f)

    #save resistivity
    date = Dates.format(Dates.now(), "yyyy-mm-dd HH")
    saveas =  directory*"resistivity_"*date
    f = open(saveas, "a+")
    print(f,"\n $Rs "*fiber.file_name)
    close(f)

    #foo = ["file_name:  " * fiber.file_name, "fiber_id:  " * fiber.fiber_id, "sample:  " * fiber.sample,"material:  " * fiber.material, "date:  " * fiber.date, "core_diameter:  " * string(fiber.core_diameter),"polished_diameter:  " * string(fiber.polished_diameter), "top_half:  " * string(fiber.top_half), "contact_spacing:  " * string(fiber.contact_spacing), "pad_number:  " * string(fiber.pad_number)]
    #writedlm(f, foo, delim='\n') #write as delimnated file


    return(r[2], "resistivity: $Rs ohms cm") #show resistance and resistivity.
end
