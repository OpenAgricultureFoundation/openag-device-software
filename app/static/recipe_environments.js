// ----- INIT -----
function initEnvironments(){
    initEnvironmentTemplate();
    initEnvironmentalHandlers();
}


function initEnvironmentTemplate(){
    console.log("Initialiing Environment Handlers");
    // For each available variable, add a form-group to the environmentTemplate
    // and Enable the "Add" environment button
    var availableVariables = getAvailableVariables();
    var template = $("#templates").children(".environment");

    for (var key in availableVariables){
        var val = availableVariables[key];
        // Add the variable to the template
        var varTemplate = $("#templates").children(".environmentVariable").clone(true);
        varTemplate.find("label").attr("for", key);
        varTemplate.find("label").text(key);
        varTemplate.find("input").attr("name", key);
        template.find('.recipe-card-body').append(varTemplate);
    }

    $("#addEnvironmentButton").removeAttr("disabled");
}


function initEnvironmentalHandlers(){
    // Add click handler to the "Add" environment button
    $("#addEnvironmentButton").click(addEnvironmentButtonHandler);
    // Add blur to environment name field to update dropdowns
    $(".environment input[name=name]").blur(environmentNameInputBlur);
}


// ----- Handlers -----
function addEnvironmentButtonHandler(event){
    // Clone the environment template and append it to the recipe-card
    console.log("Adding blank environment");
    var template = $("#templates .environment").clone(true);
    $("#environments").children(".recipe-card-body").append(template);

    // Add new environment option to the end of the environment select
    $(".environmentSelect").append("<option>New Environment</option>");
}


function environmentNameInputBlur(event){
    var jtar = $(event.target);
    var val = jtar.val();
    var ind = jtar.closest('.recipe-card').index();
    console.log("Got blur from environment " + ind + " with name " + val);

    // Update the recipe-card header
    jtar.closest('.recipe-card').find('.recipe-card-header').text(val);    

    // Update the nth option title 
    var ind1 = ind+1;  // Because nth-child is 1-offset
    $(".environmentSelect option:nth-child("+ind1+")").text(val);
}


// TODO add move up down buttons
function removeEnvironmentButtonHandler(){
    // TODO add "Remove" button and fill in code
    // Remove this environment
    // Check if any phases use this environment and clear if they do
    // (^ don't need to, will be cleared automatically)
}


// ----- Serializers -----
function getEnvironmentsJson(){
    // Returns the JSON representation of environments
    var data = [];
    $("#environments .environment").each( function( index ){
        data.push(getEnvironmentJson($(this)));
    });
    return data;
}


function getEnvironmentJson(environment){
    // Given the UI representation of a environment, convert to JSON
    var data = {};
    environment.find("input").each( function( index ){
        data[$(this).attr("name")] = $(this).val()
    });

    return data;
}


// ----- Validation -----
// TODO


// ----- Other -----
function getAvailableVariables(){
    return {
        "light_spectrum_taurus": "list",
        "light_intensity_par": "int",
        "air_temperature_celsius": "int"
    }
}

