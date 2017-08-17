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
                    sassDir: 'scss',
                    cssDir: 'css',
                    imagesDir: 'img',
                    fontsDir: 'fonts/',
                    environment: 'production',
                    specify: 'scss/design.scss',
                }
            }
        },

        concat: { // Concatenate files.
            options: {
                separator: ';',
            },
            dist: {
                src: [
                    // for including all JS: 'assets/javascripts/bootstrap/*.js',
                    'assets/javascripts/bootstrap/affix.js',
                    'assets/javascripts/bootstrap/alert.js',
                    'assets/javascripts/bootstrap/button.js',
                    'assets/javascripts/bootstrap/carousel.js',
                    'assets/javascripts/bootstrap/collapse.js',
                    'assets/javascripts/bootstrap/dropdown.js',
                    'assets/javascripts/bootstrap/tab.js',
                    'assets/javascripts/bootstrap/transition.js',
                    'assets/javascripts/bootstrap/scrollspy.js',
                    'assets/javascripts/bootstrap/modal.js',
                    'assets/javascripts/bootstrap/tooltip.js',
                    'assets/javascripts/bootstrap/popover.js',
                ],
                dest: 'js/libs/bootstrap.js',
            },
        },

        jshint: { // Validate files with JSHint.
            all: ['Gruntfile.js', 'js/*.js',],
        },

        uglify: { // Minify files with UglifyJS.
            options: {
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
                src: ['js/libs/**/*.js', 'js/*.js'],
                dest: 'js/build/script.min.js'
            }
        },

        watch: { // Run predefined tasks whenever watched files change.
            css: {
                files: ['scss/*.scss', 'scss/**/*.scss'],
                tasks: ['compass'],
                options: {
                    // Start a live reload server on the default port 35729
                    livereload: true, // <script src="//localhost:35729/livereload.js"></script>
                },
            },
            js: {
                files: ['js/libs/**/*.js', 'js/*.js', 'Gruntfile.js' ],
                tasks: ['concat', 'jshint', 'uglify', ],
                options: {
                    // Start a live reload server on the default port 35729
                    livereload: true, // <script src="//localhost:35729/livereload.js"></script>
                },
            },
            html: {
                files: ['**/*.html', '**/*.htm',],
                options: {
                    // Start a live reload server on the default port 35729
                    livereload: true, // <script src="//localhost:35729/livereload.js"></script>
                },
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
