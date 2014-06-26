crypto  = require 'crypto'
path    = require 'path'



module.exports = (grunt) ->

    PACKAGE             = grunt.file.readJSON('./package.json')
    DEBUG               = not grunt.cli.options.production
    DIST_DIR            = './.dist/'
    TO_UPLOAD_DIR       = './.dist_zip/'
    BUILD_DIR           = './static/'
    SOURCE_DIR          = './static_source/'

    nonAssetSourceFile = (src) -> grunt.file.isFile(src) and src.split('.').pop() not in ['coffee', 'sass'] and src.split(path.sep)[1]?[0] isnt '_'
    nonGzippedFile  = (src) -> grunt.file.isFile(src) and src.split('.').pop() not in ['js', 'css']

    grunt.config.init
        pkg         : PACKAGE
        BUILD_DIR   : BUILD_DIR
        SOURCE_DIR  : SOURCE_DIR

        browserify:
            app:
                src: ['<%= SOURCE_DIR %>main.coffee']
                dest: '<%= BUILD_DIR %>app.js'
                options:
                    external: []
                    # Remove this when jQuery hits 2.1.0, which will take over
                    # the 'jquery' npm package.
                    alias: ['jquery/dist/jquery:jquery']
                    transform: ['coffeeify']
                    extension: ['coffee']
                    debug: DEBUG

        compass:
            development:
                options:
                    sassDir         : SOURCE_DIR
                    cssDir          : BUILD_DIR
                    imagesDir       : SOURCE_DIR
                    extensionsDir   : 'node_modules' # For npm-installed extensions (Shiny, Formwork)
                    outputStyle     : 'expanded'

        uglify:
            options:
                compress:
                    global_defs:
                        'DEBUG': DEBUG
                    dead_code: true
                mangle: true
            production:
                files: [
                    expand  : true
                    cwd     : BUILD_DIR
                    src     : '**/*.js'
                    dest    : DIST_DIR
                ]

        watch:
            js:
                files: [SOURCE_DIR + '**/*.coffee']
                tasks: ['browserify']
            css:
                files: [SOURCE_DIR + '**/*.sass']
                tasks: ['compass:development']

        cssmin:
            production:
                files: [
                    expand  : true
                    cwd     : BUILD_DIR
                    src     : '**/*.css'
                    dest    : DIST_DIR
                ]

        # The .env files are kept separate as the .deploy.env one contains
        # more sensitive, write-access keys only ever needed to deploy. This
        # also makes it easier to set the env variables on the Heroku app.
        env:
            dev:
                src: '.env'
            deploy:
                src: '.deploy.env'

        aws_s3:
            options:
                accessKeyId     : '<%= penv.AWS_ACCESS_KEY_ID %>'
                secretAccessKey : '<%= penv.AWS_SECRET_ACCESS_KEY %>'
                region          : 'us-east-1'
            # Push the zipped assets to the CDN bucket, prefixing the keys
            # with the asset hash. Bust that cache.
            production:
                options:
                    bucket  : '<%= penv.S3_BUCKET_NAME %>'
                    action  : 'upload'
                # Two sets of files, to keep the ContentEncoding parameter
                # correct for each one. Only .js and .css files get gzipped.
                files: [
                    {
                        expand  : true
                        src     : ['**/*.js', '**/*.css']
                        dest    : '<%= penv.PUBLICATION_SHORT_NAME %>/<%= asset_hash %>/'
                        cwd     : TO_UPLOAD_DIR
                        params:
                            ContentEncoding: 'gzip'
                    }
                    {
                        expand  : true
                        src     : ['**/*']
                        dest    : '<%= penv.PUBLICATION_SHORT_NAME %>/<%= asset_hash %>/'
                        cwd     : TO_UPLOAD_DIR
                        filter  : nonGzippedFile
                    }
                ]

        # Compress .js and .css static assets using gzip.
        compress:
            options:
                mode: 'gzip'
            main:
                expand  : true
                cwd     : DIST_DIR
                src     : ['**/*.js', '**/*.css']
                dest    : TO_UPLOAD_DIR
                ext     : ''                    # Keeps the extensions the same.


        shell:
            # Update the STATIC_URL to use the new asset hash.
            setstaticurl:
                command: 'heroku config:set STATIC_URL=http://<%= penv.ASSET_CDN_ROOT %><%= penv.PUBLICATION_SHORT_NAME %>/<%= asset_hash %>/'
                options:
                    callback: (err, stdout, stderr, cb) ->
                        # The actual command can fail, while the task still
                        # succeeds. Failure is most likely because the local
                        # repository isn't configured for Heroku.
                        if err?
                            console.log err
                            console.log '\n\nIf this is not a Heroku app, it needs to be configured as such.'
                        cb()

        copy:
            dev:
                files: [
                    expand  : true
                    cwd     : SOURCE_DIR
                    src     : '**'
                    dest    : BUILD_DIR
                    filter  : nonAssetSourceFile
                ]
            # Copy to the
            production:
                files: [
                    expand  : true
                    cwd     : SOURCE_DIR
                    src     : '**'
                    dest    : TO_UPLOAD_DIR
                    filter  : nonAssetSourceFile
                ]

    # Creates an MD5 hash of the static assets to use as the cachebusting
    # STATIC_URL. The TO_UPLOAD_DIR is used so that images are included in the
    # hash calculation.
    grunt.registerTask 'hashfiles', ->
        files = grunt.file.expand(path.join(TO_UPLOAD_DIR, '**/*'))
        # Ensure the files are read in a consistent order (not that it really
        # matters too much, but no point in needlessly bustin' caches.
        files.sort()
        hash = crypto.createHash('md5')
        files.forEach (file_path) ->
            if grunt.file.isFile(file_path)
                hash.update(grunt.file.read(file_path))
        grunt.config.set('asset_hash', hash.digest('hex'))

    # Make the process.env available to other tasks. Based on
    # https://github.com/jsoverson/grunt-env/issues/4#issuecomment-15344146
    grunt.registerTask 'addprocessenv', ->
        grunt.config.set('penv', process.env)

    # Empty the static build folder, ensuring no longer created files get
    # removed, lest they end up deployed.
    grunt.registerTask 'flushstatic', ->
        if grunt.file.exists(BUILD_DIR)
            grunt.file.delete(BUILD_DIR)
        grunt.file.mkdir(BUILD_DIR)

    # Ensure the necessary folders are made for the build.
    grunt.registerTask 'preparedist', ->
        grunt.file.mkdir(DIST_DIR)
        grunt.file.mkdir(TO_UPLOAD_DIR)

    # Remove the build folders that aren't otherwise needed.
    grunt.registerTask 'cleanupdist', ->
        if grunt.file.exists(DIST_DIR)
            grunt.file.delete(DIST_DIR)
        if grunt.file.exists(TO_UPLOAD_DIR)
            grunt.file.delete(TO_UPLOAD_DIR)


    grunt.loadNpmTasks('grunt-browserify')
    grunt.loadNpmTasks('grunt-contrib-compass')
    grunt.loadNpmTasks('grunt-contrib-uglify')
    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.loadNpmTasks('grunt-contrib-cssmin')
    grunt.loadNpmTasks('grunt-contrib-compress')
    grunt.loadNpmTasks('grunt-contrib-copy')
    grunt.loadNpmTasks('grunt-env')
    grunt.loadNpmTasks('grunt-shell')
    grunt.loadNpmTasks('grunt-aws-s3')



    grunt.registerTask('build:js'       , ['browserify'])
    grunt.registerTask('build:css'      , ['compass'])
    grunt.registerTask('build'          , ['flushstatic', 'build:js', 'build:css', 'copy:dev'])
    grunt.registerTask('minify:css'     , ['cssmin'])
    grunt.registerTask('minify:js'      , ['uglify'])
    grunt.registerTask('minify'         , ['minify:js','minify:css'])
    grunt.registerTask('dev'            , ['build', 'watch'])
    grunt.registerTask('deploy:static'  , [

        'cleanupdist'       # Clean directories.
        'preparedist'

        'env'               # Load from .env and .env-deploy, & add to config.
        'addprocessenv'

        'flushstatic'       # Instead of just 'build', to avoid copying images
        'build:js'          # unnecessarily.
        'build:css'

        'copy:production'   # Copy other assets to upload folder.
        'minify'            # Minify JS and CSS assets (after copy, which may
                            # include .js or .css files).

        'compress'          # Gzip and upload the files to S3.
        'hashfiles'
        'aws_s3'

        'shell:setstaticurl' # Set the STATIC_URL for the Heroku app.

        'cleanupdist'
    ])



