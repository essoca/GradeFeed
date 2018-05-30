// JavaScript File

function addManual(n){
    var itemn = parseInt(n) + 1;
    var field = '<br><span style="color:black"> Enter manual deduction:  </span>';
    field += '<span id="demo'+ n +'" display="inline" style="color:blue"></span>';
    field += '<span id="prc'+ n +'" style="color:blue"></span>';
    field += '<div id="slidecontainer">';
    field += '<input type="range" min="1" max="100" value="1" step="1" name="manual';
    field += itemn + '" class="slider" id="range'+ n +'" onchange="showValue(this.value,'+ n +')" data-show-value="true">';
    field += '</div><br>';
    field += '<span style="color:black">Enter reason for deduction: </span><br>';
    field += '<textarea name="reason'+itemn+'" value="" rows="4" cols="30"></textarea><br>' ;
    document.getElementById('rub-defined'+n).style.display = 'none';
    document.getElementById('rub-topical'+n).innerHTML = field;
    document.getElementById('rub-topical'+n).style.display = 'inline-block';
    }
    
function showValue(newValue,n){
    var slider = document.getElementById("range"+n);
    var output = document.getElementById("demo"+n);
    output.innerHTML = slider.value;
    document.getElementById("prc"+n).innerHTML = '%';
    }
    
function range_nhi(stud){
    var add_range
    add_range = 'Enter problems not handed in: ';
    add_range += '<input type="text" name="not_handed_in" ';
    add_range += 'placeholder="e.g. all or P1,P5, or P6-">';
    add_range += '<input type="submit" value="Submit">';
    add_range += '<input type="hidden" name="student" value="'+stud+'">';
    document.getElementById('nhi').innerHTML = add_range;
    }
    
