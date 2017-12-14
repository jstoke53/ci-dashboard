xhr = null;

function startDashboardService() {
    _dashboardService = new dashboardService();
    _dashboardService.updateDashboard();
}

function dashboardService() {
    service = this;
    service.timer = null;
    service.currentPage = 1;
    service.events = null;
    service.default_branch = false;
    service.viewMode = viewMode;
    service.interval = interval;
    service.requestData = Object();

    service.start = function() {
        if(service.timer) {return;}
        service.timer = setInterval(function(){
            service.updateDashboard()} , service.interval);
    };

    service.stop = function() {
        if(xhr){xhr.abort();}
        if(!service.timer) {return;}
        clearInterval(service.timer);
        service.timer = null;
    };

    service.reset = function() {
        service.currentPage = 1;
        service.requestData = Object();
    };

    service.updateDashboard = function() {

        if(service.viewMode == 'slideshow') {
            service.requestData.page = service.currentPage;
        }

        if(service.events) {
            service.requestData.event_type = service.events;
        }

        if(service.default_branch) {
            service.requestData.default_branch = service.default_branch;
        }
        
        xhr = $.ajax({
            url: '/dashboard/fetch',
            data: service.requestData,
            beforeSend: function() {
                service.stop();
                $("#update-loader").show();
            },
            success: function(data, status, xhr) {
                $('#container').html(data);
                if(service.viewMode == 'slideshow'){
                    var number_of_pages = xhr.getResponseHeader('pages');
                    $('#pagination').html('Page ' +  service.currentPage + ' of ' + number_of_pages);
                    
                    if (xhr.getResponseHeader('last_page') == 'True') {
                        service.currentPage = 1;
                    }
                    else {
                        service.currentPage++;
                    } 
                }
            },
            complete: function() {
                service.start();
                $("#update-loader").hide();
            }
         }); 
    }
}

$(document).ready(function(){
    
    //show modal  
    $("#modal").on("shown.bs.modal", function (e) {
        _dashboardService.stop();
        var slug = e.relatedTarget.dataset.slug; 
        $.ajax({
            url: "/dashboard/modal?slug=" + slug,
            success: function (data) {
                $('.modal-content').html(data);
            },
            error: function(data) {
                var errorMsg = 'Unexpected error: ' + data.statusText;
                $('.modal-content').html(errorMsg);
            }
        });      
    });

    //hide modal
    $("#modal").on("hidden.bs.modal", function(event){
        $('.modal-content').html('<div class="modal-loading">Loading...</div>');
        _dashboardService.start();
    });

    //event filter
    $("input[name=events]").on("change", function() { 
        var filter = $('input[name=events]:checked').val();
        if(filter == 'all'){filter = null;}
        _dashboardService.reset();
        _dashboardService.events = filter;
        _dashboardService.updateDashboard();
    });

    //default branch filter
    $("input[name=default_branch]").on("change", function() { 
        var default_branch = $(this);
        $('input[name=events]').each(function() {
            $(this).attr('disabled', default_branch.prop("checked"));
            $(this).attr('checked', false);
        });

        _dashboardService.reset();
        _dashboardService.default_branch = $(this).is(":checked")
        _dashboardService.updateDashboard();       
    });
    
});