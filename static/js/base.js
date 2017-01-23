$(document).ready(function() {
    var bindButtons = function(bar) {
        var $buttons = $('#buttons button');
        $buttons.removeClass('active');

        $buttons.unbind('click');
        $buttons.on('click', function(e) {
            if (!$(this).hasClass('active')) {
                var $this = $(this).addClass('active'),
                isNo = $this.is('#vote-up');

                var vote = 0;
                if (isNo) {
                    vote = -1;
                } else {
                    vote = 1;
                }

                bar.vote = vote;
                $.post('/vote', bar);
            }
        });
    };

    $('#generate').click(function() {
        $('#header').hide();
        $('#error-image').hide();
        $('#result').hide();

        $('#loading-image').show();
        var zone = $('#zone').slider('getValue');

        $.ajax({
            url: '/bar?zone=' + zone,
            dataType: 'json',
            success: function(data) {
                $('#loading-image').hide();

                var $companyName = $('#company-name');
                $companyName.html(data.companyInfo.companyName);
                var url = null;

                if (data.homepage != null) {
                    url = data.homepage;
                } else if (data.facebook != null) {
                    url = data.facebook;
                } else {
                    url = data.companyReviews;
                }

                $companyName.attr("href", url);
                $('#station').html(data.station.name);

                var bar = {
                    'eniroId': data.eniroId,
                    'vote': 0,
                    'name': data.companyInfo.companyName,
                    'facebook': data.facebook,
                    'homepage': data.homepage,
                    'companyReviews': data.companyReviews,
                    'station': data.station.name,
                    'line': data.station.line,
                    'zone': data.station.zone
                };

                bindButtons(bar);

                $('#result').show();
            },
            error: function() {
                $('#loading-image').hide();
                $('#error-image').show();
            }
        });
    });
}) ;