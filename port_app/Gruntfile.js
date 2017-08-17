module.exports = function(grunt) {

    // Project configuration.
    grunt.initConfig({

        pkg: grunt.file.readJSON('package.json'),

        /**
         * Project plugins
         */


        compass: { // Compile Sass to CSS using Compass
            dist: {
                options: {
                    banner: '/*!\n' +
                    ' * <%= pkg.name %>\n' +
                    ' * <%= pkg.url %>\n' +
                    ' * @author <%= pkg.author %>\n' +
                    ' * @author-url <%= pkg.authorUrl %>\n' +
                    ' * @version <%= pkg.version %>\n' +
                    ' */\n',
                    relativeAssets: true,
                    sassDir: 'static/user/sass',
                    cssDir: 'static/user/css',
                    imagesDir: 'static/user/img',
                    fontsDir: 'static/user/fonts/',
                    environment: 'production',
                    specify: 'static/user/sass/main.scss'
                }
            }
        },

        concat: { // Concatenate files.
            options: {
                separator: ';',
                process: function(src, filepath) {
                    grunt.log.writeln(filepath + ' included ' );
                    return src;
                },
            },
            dist: {
                src: [
                    // 'static/back/js/vendor/**/*.min.js', // one liner
                    'static/user/js/vendor/bootstrap/bootstrap.min.js',
                    'static/user/js/vendor/jRespond/jRespond.min.js',
                    'static/user/js/vendor/d3/d3.min.js',
                    'static/user/js/vendor/d3/d3.layout.min.js',
                    'static/user/js/vendor/rickshaw/rickshaw.min.js',
                    'static/user/js/vendor/sparkline/jquery.sparkline.min.js',
                    'static/user/js/vendor/slimscroll/jquery.slimscroll.min.js',
                    'static/user/js/vendor/animsition/js/jquery.animsition.min.js',
                    'static/user/js/vendor/daterangepicker/moment.min.js',
                    'static/user/js/vendor/daterangepicker/daterangepicker.js',
                    'static/user/js/vendor/screenfull/screenfull.min.js',
                    'static/user/js/vendor/flot/jquery.flot.min.js',
                    'static/user/js/vendor/flot-tooltip/jquery.flot.tooltip.min.js',
                    'static/user/js/vendor/flot-spline/jquery.flot.spline.min.js',
                    'static/user/js/vendor/easypiechart/jquery.easypiechart.min.js',
                    'static/user/js/vendor/raphael/raphael-min.js',
                    'static/user/js/vendor/morris/morris.min.js',
                    'static/user/js/vendor/owl-carousel/owl.carousel.min.js',
                    'static/user/js/vendor/datetimepicker/js/bootstrap-datetimepicker.min.js',
                    'static/user/js/vendor/datatables/js/jquery.dataTables.min.js',
                    'static/user/js/vendor/datatables/extensions/dataTables.bootstrap.js',
                    'static/user/js/vendor/chosen/chosen.jquery.min.js',
                    'static/user/js/vendor/summernote/summernote.min.js',
                    'static/user/js/vendor/coolclock/coolclock.js',
                    'static/user/js/vendor/coolclock/excanvas.js',
                ],
                dest: 'static/user/js/libs/vendors.js',
            },
        },

        jshint: { // Validate files with JSHint.
            all: ['Gruntfile.js', 'static/user/js/*.js',],
        },

        uglify: { // Minify files with UglifyJS.
            options: {
                // beautify: true,
                mangle: {
                    except: ['jQuery',]
                },
                banner: '/*!\n' +
                ' * <%= pkg.name %>\n' +
                ' * <%= pkg.url %>\n' +
                ' * @author <%= pkg.author %>\n' +
                ' * @author-url <%= pkg.authorUrl %>\n' +
                ' * @version <%= pkg.version %>\n' +
                ' * @updated <%= grunt.template.today("yyyy-mm-dd") %> */\n'
            },
            build: {
                src: ['static/user/js/libs/**/*.js', 'static/user/js/*.js'],
                dest: 'static/user/js/build/script.min.js'
            }
        },

        /*
         * 1 line python server:
         *
         * - Python 2.x
         *   $ python -m SimpleHTTPServer 8000
         *
         * - Python 3.x
         *   $ python -m http.server 8000
         */

        watch: { // Run predefined tasks whenever watched files change.
            options: {
                livereload: true, // <script src="//localhost:35729/livereload.js"></script>
            },
            css: {
                files: ['static/user/sass/*.scss', 'static/user/sass/**/*.scss'],
                tasks: ['compass']
            },
            js: {
                files: ['static/user/js/libs/**/*.js', 'static/user/js/*.js', 'Gruntfile.js' ],
                tasks: ['concat', 'jshint', 'uglify', ]
            },
            html: {
                files: ['_html/**/*.html', '_html/**/*.htm',]
            },
        },

    });

    // Load the plugin that provides the "uglify" task.
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');

    // Default task(s).
    grunt.registerTask('default', ['uglify']);



};