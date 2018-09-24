// ----- INIT -----
function initPhases(){
    initPhaseHandlers();
}


function initPhaseHandlers(){
    console.log("Initialiing Phase Handlers");
    $("#addPhaseButton").click(addPhaseButtonHandler);
    $(".addCycleButton").click(addCycleButtonHandler);

    // Add blur to phase name field to update dropdowns
    $(".phase input[name=name]").blur(phaseNameInputBlur);
}


function addPhaseButtonHandler(event){
    console.log("Adding blank phase");
    var template = $("#templates .phase").clone(true);
    $("#phases").children(".recipe-card-body").append(template);
}


function addCycleButtonHandler(event){
    event.preventDefault();
    console.log("Adding blank cycle");
    var jtar = $(event.target);
    var template = $("#templates .cycle").clone(true);
    template.insertBefore(jtar.closest('tr'));
}


function phaseNameInputBlur(event){
    var jtar = $(event.target);
    var val = jtar.val();
    var ind = jtar.closest('.recipe-card').index();
    console.log("Got blur from phase " + ind + " with name " + val);

    // Update the recipe-card header
    jtar.closest('.recipe-card').find('.recipe-card-header').text(val);    
}


// ----- Serializers -----
function getPhasesJson(){
    // Returns the JSON representation of phases
    var data = [];
    $("#phases .phase").each( function( index ){
        data.push(getPhaseJson($(this)));
    });
    return data;
}


function getPhaseJson(phase){
    // Given the UI representation of a phase, convert to JSON
    var data = {"name": null, "repeat": null};
    for (key in data){
        data[key] = phase.find("input[name=" + key + "]").val();
    }

    data["cycles"] = [];
    phase.find('.cycle').each( function( cycleIndex ) {
        var cycleData = {};
        $(this).find("input,select").each( function( inputIndex ) {
            if ($(this).attr("type") == "number"){
                res = parseInt($(this).val());
            }
            else{
                res = $(this).val();
            }
            cycleData[$(this).attr("name")] = res;
        });
        data["cycles"].push(cycleData);
    });
    return data;
}
