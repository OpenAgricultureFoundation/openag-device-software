$(document).ready(function() {
    initCultivars();
    initEnvironments();
    initPhases();

    // Debugging, test data
    if (false) {
        console.log("Debugging!");
        $(".collapse").collapse("show");

        $("#addEnvironmentButton").click();
        $("#addEnvironmentButton").click();
        $("#addPhaseButton").click();
        $("#addPhaseButton").click();
        $(".addCycleButton").click();

        $("#templates").removeAttr("hidden");

        var arr = ["name", "briefDescription", "verboseDescription"];
        for (var i in arr){
            var x = arr[i];
            var inp = $("#details *[name=" + x + "]");
            inp.val(inp.attr("placeholder"));
        }

        $("#recipe .environment").each( function( index ){
            $(this).find("input[name=name]").val("environ" + index);
            $(this).find("input[name=name]").blur();
        });

        $("#recipe .phase").each( function( index ){
            $(this).find("input[name=name]").val("phase" + index);
            $(this).find("input[name=repeat]").val(index+1);
            $(this).find("input[name=name]").blur();
        });

        $("#recipe .cycle").each( function( index ){
            $(this).find("input[name=name]").val("cycle" + index);
            $(this).find("select[name=environment]").val("environ" + index % 2);
            $(this).find("input[name=duration_hours]").val(index+1);
        });

        $("#cultivars .searchInput").val("kale");
        $("#cultivars .searchInput").keyup();
        $("#cultivars .searchResults tbody tr td i").last().click();

        $("#cultivationMethods .searchInput").val("shallow");
        $("#cultivationMethods .searchInput").keyup();
        $("#cultivationMethods .searchResults tbody tr td i").last().click();
    }

});


// ----- Serializers -----
function getRecipeJson(){
    data = {"description": {}};

    data["name"] = $("#details input[name=name]").val();
    data["description"]["brief"] = $("#details input[name=briefDescription]").val();
    data["description"]["verbose"] = $("#details placeholder[name=verboseDescription]").val();

    
    data["cultivars"] = getCultivarsJson();
    data["cultivationMethods"] = getCultivationMethodsJson();
    data["environments"] = getEnvironmentsJson();
    data["phases"] = getPhasesJson();

    return data
}
