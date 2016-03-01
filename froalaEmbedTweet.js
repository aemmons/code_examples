/*
Custom Froala plugin to handle embedding Tweets.
*/
define(['jquery', 'twitter', 'bootstrap', 'froala-editor'
], function($){

    // Define popup template.
    $.extend($.FroalaEditor.POPUP_TEMPLATES, {
      'hbEmbedTweet.embedPopup': '[_BUTTONS_][_CUSTOM_LAYER_]',
      'hbEmbedTweet.editPopup': '[_BUTTONS_]'
    });

    // Define popup buttons.
    $.extend($.FroalaEditor.DEFAULTS, {
        tweetEmbedPopupButtons: ['hbEmbedTweetPopupClose', '|', 'hbInsertButton'],
        tweetEditPopupButtons: ['hbEditTweetPopupCloseButton', '|', 'hbDeleteTweetButton', 'hbPreviewTweetButton'],
        tweetAllowedAttrs: ['class', 'lang', 'dir', 'href'],
        tweetAllowedTags: ['blockquote', 'a'],
        defaultTweetAlignment: 'center',
        textNearTweet: true
    });

    // Define an icon and command for the button that opens the custom popup.
    $.FroalaEditor.DefineIcon('hbEmbedTweetIcon', { NAME: 'twitter'})
    $.FroalaEditor.RegisterCommand('hbEmbedTweet', {
        title: 'Embed Tweet',
        icon: 'hbEmbedTweetIcon',
        undo: false,
        focus: false,
        plugin: 'hbEmbedTweet',
        callback: function () {
          this.hbEmbedTweet.showPopup();
        }
    });

    // Define embed popup close button icon and command.
    $.FroalaEditor.DefineIcon('hbEmbedTweetPopupClose', { NAME: 'times' });
    $.FroalaEditor.RegisterCommand('hbEmbedTweetPopupClose', {
        title: 'Close',
        undo: false,
        focus: false,
        callback: function () {
            this.hbEmbedTweet.hideEmbedPopup();
        }
    });

    // Define insert button for tweet.
    $.FroalaEditor.DefineIcon('hbInsertButton', { NAME: 'sign-in' });
    $.FroalaEditor.RegisterCommand('hbInsertButton', {
        title: 'Insert',
        undo: true,
        focus: true,
        callback: function () {
          this.hbEmbedTweet.embedTweet();
          this.hbEmbedTweet.hideEmbedPopup();
        }
    });

    // Define edit popup close button icon and command.
    $.FroalaEditor.DefineIcon('hbEditTweetPopupCloseButton', { NAME: 'times' });
    $.FroalaEditor.RegisterCommand('hbEditTweetPopupCloseButton', {
        title: 'Close',
        undo: false,
        focus: false,
        callback: function () {
            this.hbEmbedTweet.hideTweetEditorPopup();
        }
    });

    // Define tweet preview button.
    $.FroalaEditor.DefineIcon('hbPreviewTweetButton', { NAME: 'eye' });
    $.FroalaEditor.RegisterCommand('hbPreviewTweetButton', {
        title: 'Preview',
        undo: false,
        focus: false,
        callback: function () {
            this.hbEmbedTweet.previewTweet();
            this.hbEmbedTweet.hideTweetEditorPopup();
        }
    });

    // Define tweet delete button.
    $.FroalaEditor.DefineIcon('hbDeleteTweetButton', { NAME: 'trash' });
    $.FroalaEditor.RegisterCommand('hbDeleteTweetButton', {
        title: 'Delete',
        undo: true,
        focus: true,
        callback: function () {
            this.hbEmbedTweet.deleteTweet();
            this.hbEmbedTweet.hideTweetEditorPopup();
        }
    });

    $.FroalaEditor.PLUGINS.hbEmbedTweet = function(editor){

        var self = {
            _$activeTweet: null
        }

        function _initTweetEmbedPopup () {
            // Load popup template.
            var template = $.FroalaEditor.POPUP_TEMPLATES['hbEmbedTweet.embedPopup'];
            if (typeof template == 'function') template = template.apply(editor);

            // Popup buttons.
            var popup_buttons = '';

            // Create the list of buttons.
            if (editor.opts.tweetEmbedPopupButtons.length > 1) {
              popup_buttons += '<div class="fr-buttons">';
              popup_buttons += editor.button.buildList(editor.opts.tweetEmbedPopupButtons);
              popup_buttons += '</div>';
            }

            // Load popup template.
            var template = {
              buttons: popup_buttons,
              custom_layer: '<div class="fr-twitter-embed-layer fr-layer fr-active" id="fr-twitter-embed-layer-'+editor.id+'"><div class="fr-input-line"><textarea type="text" placeholder="Twitter Embed Code" tabindex="1" rows="5" dir="auto" class=""></textarea><span>Twitter Embed Code</span></div><div class="f-popup-line"><span data-text="true"><a target="_blank" href="https://support.twitter.com/articles/20169559"><i class="fa fa-question-circle"></i> How to embed a Tweet</a></span></div></div>'
                  //<div class="fr-action-buttons"><button type="button" class="fr-command fr-submit" data-cmd="hbInsertButton" tabindex="2">Insert</button></div></div>'
            };

            // Create popup.
            var $popup = editor.popups.create('hbEmbedTweet.embedPopup', template);

            return $popup;
        }

        function showPopup () {
            // Get the popup object defined above.
            var $popup = editor.popups.get('hbEmbedTweet.embedPopup');

            // If popup doesn't exist then create it.
            // To improve performance it is best to create the popup when it is
            // first needed and not when the editor is initialized.
            if (!$popup) $popup = _initTweetEmbedPopup();

            // Set the editor toolbar as the popup's container.
            editor.popups.setContainer('hbEmbedTweet.embedPopup', editor.$tb);

            // Refresh the popup.
            $popup.find('textarea').attr('class', '').val('');

            // This custom popup is opened by pressing a button from the editor's toolbar.
            // Get the button's object in order to place the popup relative to it.
            var $btn = editor.$tb.find('.fr-command[data-cmd="hbEmbedTweet"]');

            // Compute the popup's position.
            var left = $btn.offset().left + $btn.outerWidth() / 2;
            var top = $btn.offset().top + (editor.opts.toolbarBottom ? 10 : $btn.outerHeight() - 10);

            // Show the custom popup.
            // The button's outerHeight is required in case the popup needs to
            // be displayed above it.
            editor.popups.show('hbEmbedTweet.embedPopup', left, top, $btn.outerHeight());
        }

          // Hide the custom popup.
        function hideEmbedPopup () {
            editor.popups.hide('hbEmbedTweet.embedPopup');
        }

        function _initTweetEditorPopup () {
            /*
             * Initialize edit popup for in-content tweets.
             */
            var template = $.FroalaEditor.POPUP_TEMPLATES['hbEmbedTweet.editPopup'];
            if (typeof template == 'function') template = template.apply(editor);

            // Popup buttons.
            var popup_buttons = '';

            // Create the list of buttons.
            if (editor.opts.tweetEditPopupButtons.length > 1) {
              popup_buttons += '<div class="fr-buttons">';
              popup_buttons += editor.button.buildList(editor.opts.tweetEditPopupButtons);
              popup_buttons += '</div>';
            }

            // Load popup template.
            var template = {
              buttons: popup_buttons
            };

            // Create popup.
            var $popup = editor.popups.create('hbEmbedTweet.editPopup', template);

            return $popup;
        }

        function showTweetEditorPopup ($tweet) {

            self._$activeTweet = $tweet;

            var $popup = editor.popups.get('hbEmbedTweet.embedPopup');

            // If popup doesn't exist then create it.
            if (!$popup) $popup = _initTweetEmbedPopup();

            editor.popups.setContainer('hbEmbedTweet.editPopup', $('body'));

            // Trigger refresh for the popup.
            editor.popups.refresh('hbEmbedTweet.editPopup');

            // Compute the popup's position.
            var left = $tweet.offset().left + $tweet.outerWidth() / 2;
            var top = $tweet.offset().top + (editor.opts.toolbarBottom ? 10 : $tweet.outerHeight() - 10);

            // Show the edit popup.
            // The tweet's outerHeight is required in case the popup needs to
            // be displayed above it.
            editor.popups.show('hbEmbedTweet.editPopup', left, top, $tweet.outerHeight());
        }

        function hideTweetEditorPopup () {
            self._$activeTweet = null;
            editor.popups.hide('hbEmbedTweet.editPopup');
        }

        function _build_tweet(code){
            /*
            Return an object with tweet html string and tweet id.
            */
            var $tweet = $($.parseHTML(code));
                id = null;

            try{
                id = $tweet.children('a').attr('href').split('/').pop();
                if(isNaN(id)) throw "not a number";
            }catch(err){
                console.log('Twitter id was not parsed correctly. ' + err);
            }

            return {
                tweet: $tweet.wrap('<div></div>').parent().html(),
                id: id
            }
        }

        function _initPopupEvent(identifier){
            /*
            * identifier can be jQuery selector string, or jQuery object.
            */
            $(identifier).click(
                function (e) {
                    e.stopPropagation();
                    editor.hbEmbedTweet.showTweetEditorPopup($(this));
                }
            );

            // Stop any links from working.
            $(identifier).find('a').click(function(e){ e.preventDefault(); });
        }

        function _initPreviewModal(){
            $modal = $('<div id="myModal" class="modal fade" tabindex="-1" role="dialog">'
                +'    <div class="modal-dialog">'
                +'        <div class="modal-content">'
                +'            <div class="modal-header">'
                +'                <button type="button" class="close" data-dismiss="modal" aria-label="Close">&times;</button>'
                +'                    <h4 class="modal-title">Tweet Preview</h4>'
                +'            </div>'
                +'            <div id="modalBody" class="modal-body">'
                +'            </div>'
                +'            <div class="modal-footer">'
                +'                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>'
                +'            </div>'
                +'        </div>'
                +'    </div>'
                +'</div>').appendTo('body');
            $modal.modal({show:false, keyboard:true})
            return $modal
        }

        function embedTweet(){
            var $el = self.$embedPopup.find('textarea'),
                val = $el.val(),
                html = '',
                tweet = _build_tweet(val),
                tweet_count = $(".fr-tweet-editor").length,
                div_id = "tweet-"+tweet_count+"-"+tweet.id;

            //insert embed code into editor.
            html = '<p><div id="'+div_id+'" contenteditable="false" class="fr-tweet-editor" data-fr-verified="true" data-hb-tweetid="'+tweet.id+'">'+tweet.tweet+'</div></p>';
            editor.html.insert(html);
            editor.undo.saveStep();

            _initPopupEvent("#"+div_id);
        }

        function deleteTweet(){
            self._$activeTweet.remove()
        }

        function previewTweet(){
            /*
            * Create lightbox style overlay to hold preview iFrame of tweet.
            */
            var tweetID = self._$activeTweet.data('hb-tweetid'),
                previewHTML = '';

            if(!self.$previewModal) self.$previewModal = _initPreviewModal();

            self.$previewModal.find('#modalBody').empty();
            window.twttr.widgets.createTweet(tweetID, document.getElementById('modalBody'), {align: 'center'})
                .then(function(el){
                    self.$previewModal.modal('show');
            });

        }

        function _init(){
            self.$embedPopup = _initTweetEmbedPopup();
            self.$editPopup = _initTweetEditorPopup();
            self.$previewModal = _initPreviewModal();

            // Attach hover events to all tweet objects on the page.
            $(".fr-tweet-editor").each(function(){
                _initPopupEvent(this);
            });

            // Attach to Undo & Redo events to re-init the tweet elements.
            $(editor.$original_element).on('froalaEditor.commands.after', function(e, editor, cmd, p1, p2){
                if(cmd=='undo' || cmd=='redo'){
                    $(".fr-tweet-editor").each(function(idx){
                        _initPopupEvent(this);
                    });
                }
            });
        }

        return {
            _init: _init,
            showPopup: showPopup,
            hideEmbedPopup: hideEmbedPopup,
            showTweetEditorPopup: showTweetEditorPopup,
            hideTweetEditorPopup: hideTweetEditorPopup,
            embedTweet: embedTweet,
            deleteTweet: deleteTweet,
            previewTweet: previewTweet
        }

    };
});
