$(document).ready(function() {
    $('#ex19').slider({
        formatter: function(value) {
            return 'Current value: ' + value;
        }
    });

    $('#generate').click(function() {
        $('#header').hide();
        $('#error-image').hide();
        $('#result').hide();
        $('#vote-up').removeClass('active');
        $('#vote-down').removeClass('active');

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

                var voteDown = function() {
                    bar.vote = -1;
                    $.post('/vote', bar);
                };

                var voteUp = function() {
                    bar.vote = 1;
                    $.post('/vote', bar);
                };

                $('#vote-up').click(function() {
                    $('#vote-down').removeClass('active');
                    if ($(this).hasClass('active')) {
                        voteDown();
                    } else {
                        voteUp();
                    }
                });
                $('#vote-down').click(function() {
                    $('#vote-up').removeClass('active');
                    if ($(this).hasClass('active')) {
                        voteUp();
                    } else {
                        voteDown();
                    }
                });

                $('#result').show();
            },
            error: function() {
                $('#loading-image').hide();
                $('#error-image').show();
            }
        });
    });
}) ;