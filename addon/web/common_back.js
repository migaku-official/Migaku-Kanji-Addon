var dmak = null;
var data = null;

function toggleShow(targetId, state) {
    var tooltipContainer = document.getElementById(targetId);

    function open() {
        tooltipContainer.style.display = 'block';
        tooltipContainer.setAttribute('aria-expanded', 'true');
    }

    function close() {
        tooltipContainer.style.display = 'none';
        tooltipContainer.setAttribute('aria-expanded', 'false');
    }

    if (typeof state === 'boolean') {
        if (state) {
            open();
        } else {
            close();
        }
    } else {
        if (tooltipContainer.style.display === 'none') {
            open();
        } else {
            close();
        }
    }
}

function toggleShowAll(state) {
    var allTooltips = document.querySelectorAll('.title-tooltip__text');

    for (var i = 0; i < allTooltips.length; i += 1) {
        var id = allTooltips[i].getAttribute('id');
        toggleShow(id, state);
    }
}

if (!settings.show_header) {
    $('.migaku-header').hide();
}
if (!settings.show_radicals) {
    $('#radicals_container').hide();
}

var noResultsSpan =
    '<span class="faded-info-msg -spaced">(no results)</span>';

var isMobileDevice = document
    .querySelector('html')
    .classList.contains('mobile');

function wrap_list(list, intro, outro, no_results_span = true) {
    if (list.length < 1) return no_results_span ? noResultsSpan : '';
    return intro + list.join(outro + intro) + outro;
}

function search(text) {
    pycmd('open-' + text);
}

function search_dict(text) {
    pycmd('search_dict-' + text);
}

function show_word_notes(notes) {
    pycmd('show_word-' + notes.join(','));
}

function primitive_click() {
    search($(this).data('character'));
}

function word_click(evt) {
    var isDictExample = $(this).hasClass('word_default');

    // - Shift + click dict lookup
    // - or, dict example click
    if (evt.shiftKey || isDictExample) {
        search_dict($(this).data('word-kanji'));
    } else if (!isDictExample) {
        var word_idx = $(this).data('word-idx');

        if (word_idx === undefined) return;

        var idx = parseInt(word_idx);

        const we = data.words[idx];
        const nids = we[2];

        show_word_notes(nids);
    }
}

function recognition_card_click(evt) {
    if (data.recognition_card_id !== null) {
        if (data.recognition_card_id < 0)
            pycmd('mark-recognition-' + data.character + '-0');
        else pycmd('show_card_id-' + data.recognition_card_id);
    } else {
        if (evt.shiftKey) pycmd('mark-recognition-' + data.character + '-1');
        else pycmd('create-recognition-' + data.character);
    }
}

function production_card_click(evt) {
    if (data.production_card_id !== null) {
        if (data.production_card_id < 0)
            pycmd('mark-production-' + data.character + '-0');
        else pycmd('show_card_id-' + data.production_card_id);
    } else {
        if (evt.shiftKey) pycmd('mark-production-' + data.character + '-1');
        else pycmd('create-production-' + data.character);
    }
}

function set_custom_keyword() {
    pycmd('custom_keyword-' + data.character);
}

function set_custom_story() {
    pycmd(
        'custom_story-' +
            data.character +
            '-' +
            (data.usr_story ? data.usr_story : ''),
    );
}

function delete_mark(evt, deck) {
    pycmd(
        'delete_mark-' +
            data.character +
            '-' + deck + '-' +
            (evt.shiftKey ? 'false' : 'true'),
    );
}

// ==================================================================
// CHANGES - START - variables and control binds

var strokeElementId = 'strokeorder',
    toggleStrokeNumberClass = '-show-stroke-numbers',
    hidePlayPauseClass = '-hide',
    $strokePlayerContainer = $('.stroke-order-diagram__player'),
    $strokeSvgContainer = $('#' + strokeElementId),
    $toggleStrokeNumber = $('#toggle_strokeorder_numbers'),
    $notchContainer = $('.stroke-order-diagram__slider-notches'),
    $slider = $('#strokeorder_slider'),
    $sliderStrokeCounter = $('.stroke-order-diagram__slider-stroke-count'),
    $playButton = $('#strokeorder_play'),
    $pauseButton = $('#strokeorder_pause'),
    $replayButton = $('#strokeorder_replay'),
    $skipStartButton = $('#strokeorder_start'),
    $skipEndButton = $('#strokeorder_end'),
    $prevButton = $('#strokeorder_prev'),
    $nextButton = $('#strokeorder_next');

function disableControls(selector) {
    var _$els = $(selector);

    _$els.each(function (idx, _el) {
        $(_el).prop('disabled', true);
    });
}

function enableControls(selector) {
    var _$els = $(selector);

    _$els.each(function (idx, _el) {
        $(_el).prop('disabled', false);
    });
}

function toggleControls(timeoutArray, selector) {
    var _$els = $(selector),
        isIdle = timeoutArray.length === 0;

    if (isIdle) {
        enableControls(selector);
    } else {
        disableControls(selector);
    }
}

function toggleStrokeOrderNumberVisibility() {
    $strokePlayerContainer.toggleClass(toggleStrokeNumberClass);
}

function clickIfNotDisabled(_$el) {
    if (_$el.prop('disabled') === false) _$el.click();
}

// "Default show stroke order numbers" in Kanji Settings window
if (settings.stroke_order_show_numbers) {
    // Note default class arrangement is as per `defaultShow=false`
    toggleStrokeOrderNumberVisibility();
}

// Control button binds
$playButton.click(function () {
    dmak.render();
});
$pauseButton.click(function () {
    $(this).prop('disabled', true);
    dmak.pause();
});
$replayButton.click(function () {
    dmak.replay();
});
$prevButton.click(function () {
    dmak.eraseLastStrokes(1);
});
$nextButton.click(function () {
    dmak.renderNextStrokes(1);
});
$skipStartButton.click(function () {
    dmak.erase();
});
$skipEndButton.click(function () {
    dmak.render(dmak.strokes.length, true);
});

// Keyboard/hotkey binds for stroke diagram navigation
$(document)
    .off('keyup.stroke-hotkey-controls') // Prevent duplicate binds
    .on('keyup.stroke-hotkey-controls', function (e) {
        // Left arrow key
        if (e.which === 37) {
            if (e.ctrlKey) {
                clickIfNotDisabled($skipStartButton);
            } else {
                clickIfNotDisabled($prevButton);
            }

            // Right arrow key
        } else if (e.which === 39) {
            if (e.ctrlKey) {
                clickIfNotDisabled($skipEndButton);
            } else {
                clickIfNotDisabled($nextButton);
            }
        }
    });

// Toggle stroke order number visibility
$toggleStrokeNumber.on('click', toggleStrokeOrderNumberVisibility);

// CHANGES - END - variables and control binds
// ==================================================================

function render_page(page_type) {

    if (page_type != 'lookup') {
        var data_b64 = document.getElementById('migaku_data').innerHTML;
        data_b64 = data_b64.replace(/(<([^>]+)>)/gi, ''); // Needed because of Migaku Editor :|
        var data_json = atob(data_b64);
        data = JSON.parse(data_json);
    }

    // ==================================================================
    // CHANGES - START - stroke order diagram

    dmak_parameters = {
        element: strokeElementId,
        uri: page_type == 'lookup' ? kanjivg_supplementary_uri : '',
        secondary_uri: page_type == 'lookup' ? kanjivg_uri : '',
        height: 220,
        width: 220,
        step: 0.015,

        // Always false - "autoplay" default/variable is set below
        autoplay: false,

        // Always on - toggled via CSS (and default set below)
        stroke: { order: { visible: true } },

        // Grid is manually drawn in CSS instead
        grid: { show: false },

        startedErasing: function (self, strokeNum) {
            // Keep slider value up to date
            $slider.val(self.pointer);
            $slider.data('prev', self.pointer);
            $sliderStrokeCounter.text(strokeNum);

            disableControls('[data-disable-while-erasing]');

            if (strokeNum === 0) {
                $prevButton.prop('disabled', true);
                $skipStartButton.prop('disabled', true);
            }
        },
        finishedErasing: function (self, strokeNum) {
            enableControls('[data-disable-while-erasing]');

            if (strokeNum === self.strokes.length) {
                $playButton.addClass(hidePlayPauseClass);
                $replayButton.removeClass(hidePlayPauseClass);
            } else {
                $playButton.removeClass(hidePlayPauseClass);
                $replayButton.addClass(hidePlayPauseClass);
            }
        },
        startedDrawing: function (self, strokeNum) {
            // Keep slider value up to date
            $slider.val(strokeNum);
            $slider.data('prev', strokeNum);
            $sliderStrokeCounter.text(strokeNum);

            $replayButton.addClass(hidePlayPauseClass);

            if (self.state.isRenderingSequential) {
                $playButton.addClass(hidePlayPauseClass);
                $pauseButton.removeClass(hidePlayPauseClass);
                $pauseButton.prop('disabled', false);

                disableControls('[data-disable-while-playing]');
            } else {
                $playButton.removeClass(hidePlayPauseClass);
                $pauseButton.addClass(hidePlayPauseClass);

                disableControls('[data-disable-while-drawing]');
            }

            if (strokeNum === self.strokes.length) {
                $nextButton.prop('disabled', true);
                $skipEndButton.prop('disabled', true);
            }
        },
        finishedDrawing: function (self) {
            if (self.state.wasRenderingSequential) {
                toggleControls(self.timeouts.play, '[data-disable-while-playing]');

                $nextButton.prop('disabled', true);
                $skipEndButton.prop('disabled', true);
            } else if (!self.state.isRendering) {
                        toggleControls(
                            self.timeouts.drawing,
                            '[data-disable-while-drawing]',
                        );
            }

            $pauseButton.addClass(hidePlayPauseClass);

            if (self.pointer === self.strokes.length) {
                $playButton.addClass(hidePlayPauseClass);
                $replayButton.removeClass(hidePlayPauseClass);
            } else {
                $playButton.removeClass(hidePlayPauseClass);
                $replayButton.addClass(hidePlayPauseClass);
            }
        },
        loaded: function (self) {
            var total_strokes = self.strokes.length;

            $slider.attr('max', total_strokes);
            $slider.data('prev', total_strokes); // Cache starting value

            // "Stroke order play mode" in Kanji Settings window
            if (settings.stroke_order_mode === 'auto') {
                // Draw strokes one by one
                self.render(total_strokes);
                $sliderStrokeCounter.text(0);
            } else if (settings.stroke_order_mode === 'auto_all') {
                // Draw all strokes at once
                self.render(total_strokes, true); // simultaneous = true
                $sliderStrokeCounter.text(total_strokes);
            } else if (settings.stroke_order_mode !== 'noplay') {
                // Draw all strokes at once for quick rendering
                self.render(total_strokes, true, true); // simultaneous = true, instant = true
                $sliderStrokeCounter.text(total_strokes);
            }

            // Important for the lookup browser, lest notches accumulate
            $notchContainer.empty();

            // +1 to include notch at the "0" stroke mark
            for (var i = 0; i < total_strokes + 1; i++) {
                $notchContainer.append($('<span class="slider-notch"></span>'));
            }

            $slider.on('change', function (event) {
                // Forced typecasting necessary to retain consistent performance
                // in Anki - likely a relic of the Anki JS/browser version !! dont change !!
                var stroke_num = parseInt($slider.val().toString()),
                    prev_stroke_num = parseInt($slider.data('prev').toString()),
                    shouldErase = $(this).val() < $slider.data('prev'),
                    shouldDraw = $(this).val() > $slider.data('prev'),
                    didAct = false;

                // Erase/draw as appropriate, to the selected stroke
                if (shouldErase || shouldDraw) {
                    didAct = true;

                    if (shouldErase) {
                        dmak.erase(stroke_num);
                    } else if (shouldDraw) {
                        dmak.render(stroke_num, true);
                    }
                }

                if (didAct) {
                    // Save the currently selected stroke for next comparison
                    $slider.data('prev', stroke_num);
                } else {
                    // Proactively prevent any visual side-effects if somehow
                    // the slider value change doesn't trigger dmak draw/erase
                    $slider.val(prev_stroke_num);
                }
            });
        },
    }

    if (page_type != "lookup") {
        // Preload SVG data from card fields
        dmak_parameters['preload_svgs'] =  { '{{Character}}': `{{StrokeOrder}}` } 
    } 

    dmak = new Dmak(data.character, dmak_parameters);

    // CHANGES - END - stroke order diagram
    // ==================================================================

    if (page_type == "recognition") {
        $('.keyword-kanji').html(ReplaceTagsWithImages(data.character));
    }
    $('.fontExample').html(ReplaceTagsWithImages(data.character));

    tags = [];
    if (data.frequency_rank < 999999)
        tags.push('Frequency #' + data.frequency_rank.toString());
    if (data.jlpt !== null) tags.push('JLPT N' + data.jlpt.toString());
    if (data.kanken !== null) tags.push('Kanken ' + data.kanken.toString());
    if (data.grade !== null) {
        const num_conv = '０１２３４５６７８９';
        if (data.grade <= 6) tags.push('小学校' + num_conv[data.grade] + '年');
        if (data.grade == 8) tags.push('中学年');
        if (data.grade <= 8) tags.push('常用');
        if (data.grade >= 9 && data.grade <= 10) tags.push('人名用');
    }
    if (data.heisig_id5 !== null)
        tags.push('RTK (1-5) ' + data.heisig_id5.toString());
    if (data.heisig_id6 !== null)
        tags.push('RTK (6+) ' + data.heisig_id6.toString());
    if (data.wk !== null) tags.push('WK ' + data.wk.toString());

    $('.tags').html(wrap_list(tags, '<div class="tag">', '</div>', false));

    $('#onyomi').html(data.onyomi.length ? data.onyomi.join(', ') : '-');
    $('#kunyomi').html(data.kunyomi.length ? data.kunyomi.join(', ') : '-');
    $('#nanori').html(data.nanori.length ? data.nanori.join(', ') : '-');

	var primitives_pts = [];
	for (const p_data of data.primitives_detail) {
		var keywords = [];
        if (!p_data.has_result) {
            primitives_pts.push('MISSING DATA FOR ' + p_data.character);
            continue
        }
        if (p_data.usr_keyword) keywords.push(p_data.usr_keyword);
        if (
            p_data.heisig_keyword5 &&
            !keywords.includes(p_data.heisig_keyword5)
        )
            keywords.push(p_data.heisig_keyword5);
        if (
            p_data.heisig_keyword6 &&
            !keywords.includes(p_data.heisig_keyword6)
        )
        keywords.push(p_data.heisig_keyword6);
		if (p_data.usr_primitive_keyword)
			keywords.push(
				'<span class="primitive_keyword">' +
					p_data.usr_primitive_keyword +
					'</span>',
			);
		for (const pk of p_data.primitive_keywords) {
			const kw = '<span class="primitive_keyword">' + pk + '</span>';
			if (!keywords.includes(kw)) keywords.push(kw);
		}
		var keywords_txt = keywords.length ? keywords.join(', ') : '-';

		var meanings_txt = p_data.meanings.length
			? p_data.meanings.join(', ')
			: '-';

            var primitiveHasAlts = p_data.primitive_alternatives.length > 0
            var new_primitive_alternatives = []
            if (primitiveHasAlts) {
                for (const prim_alt of p_data.primitive_alternatives) {
                    new_primitive_alternatives.push(ReplaceTagsWithImages(prim_alt))
                }
            }
            primitive_alternatives_txt = primitiveHasAlts
                ? new_primitive_alternatives.join(', ')
                : '-';

		primitives_pts.push(
			`<button
					class="primitive${primitiveHasAlts ? ' -has-alternative' : ''}"
					data-character="${p_data.character}"
				>
                    ${ReplaceTagsWithImages(p_data.character)}
                    <div class="primitiveDetails">
						<div class="primitiveDetails-keywords">
							<h3>Keywords:</h3>
							<span>${keywords_txt}</span>
						</div>
						<div class="primitiveDetails-meanings">
							<h3>Meanings:</h3>
							<span>${meanings_txt}</span>
						</div>
						<div class="primitiveDetails-alternatives">
							<h3><h3>${primitiveHasAlts ? '*' : ''}Alternatives:</h3></h3>
							<span>${primitive_alternatives_txt}</span > </div>
			</div>
		</button>`,
		);
	}

	var hasPrimitives = primitives_pts.length > 0;
	$('#primitives').empty();
	$('#primitives').html(
		hasPrimitives ? primitives_pts.join('') : noResultsSpan,
	);

	var primitive_of_pts = [];
	for (const p_data of data.primitive_of_detail) {
		var keywords = [];
        if (!p_data.has_result) {
            primitives_pts.push('MISSING DATA FOR ' + p_data.character);
            continue
        }
        if (p_data.usr_keyword) keywords.push(p_data.usr_keyword);
        if (
            p_data.heisig_keyword5 &&
            !keywords.includes(p_data.heisig_keyword5)
        )
            keywords.push(p_data.heisig_keyword5);
        if (
            p_data.heisig_keyword6 &&
            !keywords.includes(p_data.heisig_keyword6)
        )
            keywords.push(p_data.heisig_keyword6);
        if (p_data.usr_primitive_keyword)
			keywords.push(
				'<span class="primitive_keyword">' +
					p_data.usr_primitive_keyword +
					'</span>',
			);
		for (const pk of p_data.primitive_keywords) {
			const kw = '<span class="primitive_keyword">' + pk + '</span>';
			if (!keywords.includes(kw)) keywords.push(kw);
		}
		var keywords_txt = keywords.length ? keywords.join(', ') : '-';

		var meanings_txt = p_data.meanings.length
			? p_data.meanings.join(', ')
			: '-';

        var primitiveOfHasAlts = p_data.primitive_alternatives.length > 0
        var new_primitive_alternatives = []
        if (primitiveOfHasAlts) {
            for (const prim_alt of p_data.primitive_alternatives) {
                new_primitive_alternatives.push(ReplaceTagsWithImages(prim_alt))
            }
        }
        primitive_alternatives_txt = primitiveHasAlts
            ? new_primitive_alternatives.join(', ')
            : '-';

		primitive_of_pts.push(
			`<button
					class="primitive${primitiveOfHasAlts ? ' -has-alternative' : ''}"
					data-character="${p_data.character}"
				>
                    ${ReplaceTagsWithImages(p_data.character)}
                    <div class="primitiveDetails">
						<div class="primitiveDetails-keywords">
							<h3>Keywords:</h3>
							<span>${keywords_txt}</span>
						</div>
						<div class="primitiveDetails-meanings">
							<h3>Meanings:</h3>
							<span>${meanings_txt}</span>
						</div>
						<div class="primitiveDetails-alternatives">
							<h3>${primitiveOfHasAlts ? '*' : ''}Alternatives:</h3>
							<span>${primitive_alternatives_txt}</span > </div>
			</div>
		</button>`,
		);
	}

	var hasPrimitivesOf = primitive_of_pts.length > 0;
	$('#primitives_of').empty();
	$('#primitive_of').html(
		hasPrimitivesOf ? primitive_of_pts.join('') : noResultsSpan,
	);

    var kanjiHasPrimitiveAlts = data.primitive_alternatives.length > 0;
    $('#primitive_of_alts').hide();
    $('#primitive_of_alts .primitive-alternatives').empty();

    if (kanjiHasPrimitiveAlts) {
        var new_primitive_alternatives = []
        if (kanjiHasPrimitiveAlts) {
            for (const prim_alt of data.primitive_alternatives) {
                new_primitive_alternatives.push(ReplaceTagsWithImages(prim_alt))
            }
        }
        $('#primitive_of_alts').show();
        $('#primitive_of_alts .primitive-alternatives').html(
            new_primitive_alternatives.join(', '),
        );
    }

    $('.primitive').click(primitive_click);

    // Truncate results with "show more" button (if applicable)
    var primitive_of_max = 10;
    if (primitive_of_pts.length > primitive_of_max) {
        const _$showMoreBtn = $(
            '<button type="button" class="show-more__button"></button>',
        );

        // Change button text/data to reflect show more/less behaviour
        function setShowMoreLessBtn(moreOrLess, _$btn) {
            const shouldShowMore = moreOrLess === 'more';

            _$btn.html(
                `${
                    shouldShowMore
                        ? `more<br/>(${primitive_of_pts.length - primitive_of_max})`
                        : 'show<br/>less'
                }`,
            );
            _$btn.data('show-more-less', shouldShowMore ? 'more' : 'less');
        }

        // Default hide surplus results
        $(`#primitive_of .primitive:nth-child(n+${primitive_of_max + 1})`).hide();
        setShowMoreLessBtn('more', _$showMoreBtn);

        // Click event listener to toggle show more/less
        _$showMoreBtn.click(function () {
            const moreOrLess = _$showMoreBtn.data('show-more-less');
            const shouldShowMore = moreOrLess === 'more';

            if (moreOrLess === 'more') {
                $(
                    `#primitive_of .primitive:nth-child(n+${primitive_of_max + 1})`,
                ).show();
                setShowMoreLessBtn('less', _$showMoreBtn);
            } else if (moreOrLess === 'less') {
                $(
                    `#primitive_of .primitive:nth-child(n+${primitive_of_max + 1})`,
                ).hide();
                setShowMoreLessBtn('more', _$showMoreBtn);
            }
        });

        $('#primitive_of').append(_$showMoreBtn);
    }

    var max_words_front = settings.words_max;
    var word_pts = [];
    var word_front_pts = [];

    for (var i = 0; i < data.words.length; i++) {
        const we = data.words[i];
        const w = we[0];
        const r = we[1];
        const n = we[3];

        let classes = ['word'];
        let front_classes = ['word_front'];
        if (n) {
            classes.push('word_new');
            front_classes.push('word_front_default');
        }

        word_pts.push(
            `
            <button type="button" class="${classes.join(
                ' ',
            )}" data-word-kanji="${w}" data-word-idx="${i}">
                ${JapaneseUtil.distributeFuriganaHTML(w, r)}
                <span class="selectable-text" aria-hidden="true">${w}</span>
                ${
                    isMobileDevice
                        ? `<a
                            href="https://jisho.org/search/${encodeURI(w)}"
                            target="_blank"
                            class="jisho-search"
                            aria-hidden="true"
                            rel="noopener noreferrer"
                        ></a>`
                        : ''
                }
            </button>
        `,
        );

        if (
            !(n && settings.hide_default_words) &&
            word_front_pts.length < max_words_front
        )
            word_front_pts.push(
                `<div class="${front_classes.join(' ')}">` +
                    JapaneseUtil.distributeFuriganaHTML(w, r) +
                    '</div>',
            );
    }
    for (var i = 0; i < data.words_default.length; i++) {
        const we = data.words_default[i];
        const w = we[0];
        const r = we[1];

        if (
            data.words.some(function (existing_we) {
                return w == existing_we[0] && r == existing_we[1];
            })
        )
            continue;

        word_pts.push(
            `
            <button type="button" class="word word_default" data-word-kanji="${w}">
                ${JapaneseUtil.distributeFuriganaHTML(w, r)}
                <span class="selectable-text" aria-hidden="true">${w}</span>
                ${
                    isMobileDevice
                        ? `<a
                            href="https://jisho.org/search/${encodeURI(w)}"
                            target="_blank"
                            class="jisho-search"
                            aria-hidden="true"
                            rel="noopener noreferrer"
                        ></a>`
                        : ''
                }
            </button>
        `,
        );

        if (!settings.hide_default_words && word_front_pts.length < max_words_front)
            word_front_pts.push(
                '<div class="word_front word_front_default">' +
                    JapaneseUtil.distributeFuriganaHTML(w, r) +
                    '</div>',
            );
    }

    var hasLinkedWords = word_pts.length > 0;

    // Only show contained info messages if there are results returned
    var _$containedLinkedWordsInfoMsgs = $('#words')
        .parents('.results-container')
        .find('.faded-info-msg');
    _$containedLinkedWordsInfoMsgs.each(function (idx, msg) {
        $(msg).toggle(hasLinkedWords);
    });

    // Inject linked words into the DOM
    $('#words').empty();
    $('#words').html(hasLinkedWords ? word_pts.join('') : noResultsSpan);
    if (page_type != "lookup") {
        $('#words_front').html(word_front_pts.join(''));
    }

    // Truncate results with "show more" button (if applicable)
    var words_max = 10;
    if (word_pts.length > words_max) {
        const _$showMoreBtn = $(
            '<button type="button" class="show-more__button"></button>',
        );

        // Change button text/data to reflect show more/less behaviour
        function setShowMoreLessBtn(moreOrLess, _$btn) {
            const shouldShowMore = moreOrLess === 'more';

            _$btn.html(
                `Show<br/>${moreOrLess}<br/>${
                    shouldShowMore ? `(${word_pts.length - words_max})` : ''
                }`,
            );
            _$btn.data('show-more-less', shouldShowMore ? 'more' : 'less');
        }

        // Default hide surplus results
        $(`#words .word:nth-child(n+${words_max + 1})`).hide();
        setShowMoreLessBtn('more', _$showMoreBtn);

        // Click event listener to toggle show more/less
        _$showMoreBtn.click('click', function () {
            const moreOrLess = _$showMoreBtn.data('show-more-less');
            const shouldShowMore = moreOrLess === 'more';

            if (moreOrLess === 'more') {
                $(`#words .word:nth-child(n+${words_max + 1})`).show();
                setShowMoreLessBtn('less', _$showMoreBtn);
            } else if (moreOrLess === 'less') {
                $(`#words .word:nth-child(n+${words_max + 1})`).hide();
                setShowMoreLessBtn('more', _$showMoreBtn);
            }
        });

        $('#words').append(_$showMoreBtn);
    }

    // Optionally apply hover-only furigana styles
    $('#words').toggleClass(
        'hide_readings_hover',
        settings.hide_readings_hover,
    );

    if (isMobileDevice) {
        // Simulating a click on a real hyperlink is the only way to reliably open
        // the native/default web browser on both AnkiDroid and iOS. Doing it this
        // way, rather than rendering a hyperlink (instead of a button) is necessary
        // to have consistent styles, and to retain ability to reliably copy/paste link
        // text without link preview pop-ups interfering on iOS. A bit hacky.
        $('.word').click(function () {
            // New/unknown words have additional classes appended
            var isKnownWord = this.classList.length === 1,
                revealOnHoverIsSet = settings.hide_readings_hover,
                hasntAlreadyBeenRevealed = !$(this).data('is-revealed');

            // If the hide "readings on hover" setting has been enabled:
            // 1. reveal furigana on first tap
            // 2. search jisho.org on second tap
            if (isKnownWord && revealOnHoverIsSet && hasntAlreadyBeenRevealed) {
                $(this).data('is-revealed', true);
                $(this).addClass('-reveal-reading');
            } else {
                // It's necessary to use vanilla JS here, since
                // jQuery's equivalent `click()` function doesnt work
                this.querySelector('a.jisho-search').click();
            }
        });
    } else {
        // Open Anki card browser on desktop
        $('.word').click(word_click);
    }

    if (page_type == "production") {        
        if (settings.hide_keywords && word_front_pts.length > 0)
            document.getElementById('keywords_front').style.display = 'none';
    }

    var hasRadicals = data.radicals.length > 0;
    // Only show contained info messages if there are results returned
    var _$containedRadicalInfoMsgs = $('#radicals')
        .parents('.results-container')
        .find('.faded-info-msg');
    _$containedRadicalInfoMsgs.each(function (idx, msg) {
        $(msg).toggle(hasRadicals);
    });

    $('#radicals').empty();
    $('#radicals').html(
        wrap_list(data.radicals, '<button class="radical">', '</button>'),
    );

    var keywords = [];
    if (data.usr_keyword) keywords.push(data.usr_keyword);
    if (!settings.only_custom_keywords || keywords.length < 1 || page_type == "lookup") {
        if (data.heisig_keyword5 && !keywords.includes(data.heisig_keyword5))
            keywords.push(data.heisig_keyword5);
        if (data.heisig_keyword6 && !keywords.includes(data.heisig_keyword6))
            keywords.push(data.heisig_keyword6);
        if (data.usr_primitive_keyword)
            keywords.push(
                '<span class="primitive_keyword">' +
                    data.usr_primitive_keyword +
                    '</span>',
            );
        for (const pk of data.primitive_keywords) {
            const kw = '<span class="primitive_keyword">' + pk + '</span>';
            if (!keywords.includes(kw)) keywords.push(kw);
        }
    }
    keywords_txt = keywords.length ? keywords.join(', ') : '-';
    $('#keywords').html(keywords_txt);
    if (keywords.length < 1) keywords = data.meanings;
    keywords_front_txt = keywords.length ? keywords.join(', ') : '-';
    if (page_type != "lookup") {
        $('#keywords_front').html(keywords_front_txt); }

    var meanings_txt = data.meanings.length ? data.meanings.join(', ') : '-';
    $('#meanings').html(meanings_txt);
    if (page_type == "recognition") {
        if (data.meanings.length) $('#meanings_front').html(meanings_txt);
    }

	var stories = [];
	if (data.usr_story) stories.push(data.usr_story.split('\n').join('<br>'));
	if (!settings.only_custom_stories || stories.length < 1 || page_type == 'lookup') {
        if (data.heisig_story) {
            var heisig_story = data.heisig_story;
            stories.push(ReplaceTagsWithImages(heisig_story));
        }
        if (data.heisig_comment) {
            var detagged_heisig_comment = ReplaceTagsWithImages(data.heisig_comment)
            if (data.heisig_story) {
                detagged_heisig_comment = '<br><br>' + detagged_heisig_comment
            }			
            stories.push(detagged_heisig_comment)
        }
		for (const ks of data.koohi_stories) stories.push(ks);
	}

    $('#stories').html(wrap_list(stories, '<p class="story">', '</p>'));

    if (page_type == "lookup") {

        function setup_card_btn(id, data, name) {
            txt = '';
            title = null;
            if (data === null) {
                txt = 'Create ' + name + ' Card';
                title = 'Shift click to mark as known';
            }
            if (data > 0) txt = 'Show ' + name + ' Card';
            if (data < 0) txt = 'Unmark ' + name + ' as known';

            $(id).html(txt);
            $(id).prop('title', title);
        }

        setup_card_btn(
            '#recognition_card_btn',
            data.recognition_card_id,
            'Recognition',
        );
        setup_card_btn(
            '#production_card_btn',
            data.production_card_id,
            'Production',
        );

        $('.userDataEntry').remove();
        for (key in data.user_data) {
            var user_data_raw = data.user_data[key].trim();

            if (user_data_raw.length) {
                var user_data_elem = document.createElement('div');
                user_data_elem.innerHTML = user_data_raw;
                user_data_elem.classList.add('userDataEntry');

                $('.userData').append(user_data_elem);
            }
        }
        $('.userData').toggle($('.userDataEntry').length > 0);
    }
}
