#
# Authentic Theme 9.0.3 (https://github.com/qooob/authentic-theme)
# Copyright 2015 Ilia Rostovtsev <programming@rostovtsev.ru>
# Licensed under MIT (https://github.com/qooob/authentic-theme/blob/master/LICENSE)
#

BEGIN { push( @INC, ".." ); }
use WebminCore;
&ReadParse();
&init_config();

do "authentic-theme/authentic-lib.cgi";

&load_theme_library();
use Time::Local;
( $hasvirt, $level, $hasvm2 ) = get_virtualmin_user_level();
%text = &load_language($current_theme);
%text = ( &load_language('virtual-server'), %text );

&header($title);
print '<div id="wrapper" class="page" data-notice="'
    . (( -f $root_directory . '/authentic-theme/update' ) ? _post_install() : '0') . '">' . "\n";
print '<div class="container">' . "\n";
print '<div id="system-status" class="panel panel-default">' . "\n";
print '<div class="panel-heading">' . "\n";
print '<h3 class="panel-title">' . &text('body_header0') . (
    ( $level != 2 && $level != 3 && &foreign_available("webmin") )
    ? '<a href="/?updated" target="_top" data-href="'
        . $gconfig{'webprefix'}
        . '/webmin/edit_webmincron.cgi" data-refresh="system-status" class="btn btn-success pull-right" style="margin:-6px -11px;color: white"><i class="fa fa-refresh"></i></a>
        <button type="button" class="btn btn-primary" style="display: none; visibility: hidden" data-toggle="modal" data-target="#update_notice"></button>'
    : ''
) . '</h3>' . "\n";

print '</div>';
print '<div class="panel-body">' . "\n";

if ( $level == 0 ) {

    # Ask status module for collected info
    &foreign_require("system-status");
    $info = &system_status::get_collected_info();

    # Circle Progress Container
    print '<div class="row" style="margin: 0;">' . "\n";
    $col_width = &get_col_num( $info, 12 );

    # CPU Usage
    if ( $info->{'cpu'} ) {
        @c    = @{ $info->{'cpu'} };
        $used = $c[0] + $c[1] + $c[3];
        &print_progressbar_colum( 6, $col_width, $used, 'CPU' );
    }

    # MEM e VIRT Usage
    if ( $info->{'mem'} ) {
        @m = @{ $info->{'mem'} };
        if ( @m && $m[0] ) {
            $used = ( $m[0] - $m[1] ) / $m[0] * 100;
            &print_progressbar_colum( 6, $col_width, $used, 'MEM' );
        }
        if ( @m && $m[2] ) {
            $used = ( $m[2] - $m[3] ) / $m[2] * 100;
            &print_progressbar_colum( 6, $col_width, $used, 'VIRT' );
        }
    }

    # HDD Usage
    if ( $info->{'disk_total'} ) {
        ( $total, $free ) = ( $info->{'disk_total'}, $info->{'disk_free'} );
        $used = ( $total - $free ) / $total * 100;
        &print_progressbar_colum( 6, $col_width, $used, 'HDD' );
    }
    print '</div>' . "\n";

    # Info table
    print '<table class="table table-hover">' . "\n";

    # Hostname Info
    $ip
        = $info && $info->{'ips'}
        ? $info->{'ips'}->[0]->[0]
        : &to_ipaddress( get_system_hostname() );
    $ip = " ($ip)" if ($ip);
    $host = &get_system_hostname() . $ip;
    if ( &foreign_available("net") ) {
        $host
            = '<a href="'
            . $gconfig{'webprefix'}
            . '/net/list_dns.cgi">'
            . $host . '</a>';
    }
    &print_table_row( &text('body_host'), $host );

    # Operating System Info
    if ( $gconfig{'os_version'} eq '*' ) {
        $os = $gconfig{'real_os_type'};
    }
    else {
        $os = $gconfig{'real_os_type'} . ' ' . $gconfig{'real_os_version'};
    }
    &print_table_row( &text('body_os'), $os );

    # Webmin version
    &print_table_row( &text('body_webmin'), &get_webmin_version() );

    # Virtualmin version
    if ($hasvirt) {
        if ($hasvirt
            && read_env_file( $virtual_server::virtualmin_license_file,
                \%vserial )
            && $vserial{'SerialNumber'} ne 'GPL'
            )
        {
            $license = 1;

            # Parse license expiry date
            my %lstatus;
            read_file( $virtual_server::licence_status, \%lstatus );

            if ( $lstatus{'used_servers'} ) {
                $right_licensed_virtualmin_systems_text = $text{'right_smax'};
                $right_licensed_virtualmin_systems_data
                    = $lstatus{'servers'} || $text{'right_vunlimited'};
                $right_licensed_virtualmin_systems_installed_on_text
                    = $text{'right_sused'};
                $right_licensed_virtualmin_systems_installed_on_data
                    = $lstatus{'used_servers'};

            }

            if ( $lstatus{'expiry'} =~ /^203[2-8]-/ ) {
                $right_expiry_text = $text{'right_expiry'};
                $right_expiry_data = $text{'right_expirynever'};
            }
            elsif ( $lstatus{'expiry'} ) {
                $right_expiry_text = $text{'right_expiry'};
                $right_expiry_data = $lstatus{'expiry'};

                $ltm = &parse_license_date( $lstatus{'expiry'} );
                if ($ltm) {
                    $days = int( ( $ltm - time() ) / ( 24 * 60 * 60 ) );
                    $right_expiry_until_text = $text{'right_expirydays'};
                    $right_expiry_until_data
                        = $days < 0
                        ? &text( 'right_expiryago', -$days )
                        : $days;
                }
            }
        }
        else {
            $license = 0;
        }
        if ( $license == 1 ) {
            ( $dleft, $dreason, $dmax, $dhide )
                = virtual_server::count_domains("realdoms");
        }
        print_table_row(
            $text{'right_virtualmin'},
            $virtual_server::module_info{'version'} . " " . (
                $virtual_server::module_info{'virtualmin'} eq 'gpl'
                ? ''
                : 'Pro'

                    . (
                    ( $license == 1 )
                    ? '<button class="btn btn-default btn-xs btn-hidden hidden"  data-toggle="virtualmin-license" data-placement="top" title="'
                        . $text{'right_licenceheader'}
                        . '" style="margin-left:6px; padding:0 8px; line-height: 12px; height:15px;font-size:11px"

                        data-proc-serial-number-text="'
                        . $text{'right_vserial'} . '"
                        data-proc-serial-number-data="'
                        . $vserial{'SerialNumber'} . '"

                        data-proc-license-key-text="'
                        . $text{'right_vkey'} . '"
                        data-proc-license-key-data="'
                        . $vserial{'LicenseKey'} . '"

                        data-proc-license-domains-text="'
                        . $text{'right_vmax'} . '"
                        data-proc-license-domains-data="'
                        . ( $dmax <= 0 ? $text{'right_vunlimited'} : $dmax )
                        . '"

                        data-proc-license-domains-left-text="'
                        . $text{'right_vleft'} . '"
                        data-proc-license-domains-left-data="'
                        . (
                          $dleft < 0
                        ? $text{'right_vunlimited'}
                        : $dleft
                        )
                        . '"

                        data-proc-licensed-virtualmin-systems-text="'
                        . $right_licensed_virtualmin_systems_text . '"
                        data-proc-licensed-virtualmin-systems-data="'
                        . $right_licensed_virtualmin_systems_data . '"

                        data-proc-licensed-virtualmin-systems-installed-on-text="'
                        . $right_licensed_virtualmin_systems_installed_on_text
                        . '"
                        data-proc-licensed-virtualmin-systems-installed-on-data="'
                        . $right_licensed_virtualmin_systems_installed_on_data
                        . '"

                        data-proc-expiry-date-text="'
                        . $right_expiry_text . '"
                        data-proc-expiry-date-data="'
                        . $right_expiry_data . '"

                        data-proc-expiry-days-text="'
                        . $right_expiry_until_text . '"
                        data-proc-expiry-days-data="'
                        . $right_expiry_until_data . '"

                       >
                        <i class="fa fa-info"></i>
                       </button>'
                        . '<a class="btn btn-default btn-xs btn-hidden hidden" data-toggle="tooltip" data-placement="top" title="'
                        . $text{'right_vlcheck'}
                        . '" style="margin-left:1px;padding:0 6px; line-height: 12px; height:15px;font-size:11px" href="'
                        . $gconfig{'webprefix'}
                        . '/virtual-server/licence.cgi"><i class="fa fa-refresh"></i></a>'
                    : ''
                    )

            )
        );
    }

    # Cloudmin version
    if ($hasvm2) {
        print_table_row(
            $text{'right_vm2'},
            $server_manager::module_info{'version'} . " "
                . (
                $server_manager::module_info{'virtualmin'} eq 'gpl'
                ? ''
                : 'Pro'
                )
        );

        # The rest will be added later
    }

    # Theme version/updates
    # Define installed version
    open my $authentic_installed_version, '<',
        $root_directory . "/authentic-theme/VERSION.txt";
    my $installed_version = <$authentic_installed_version>;
    close $authentic_installed_version;

    # Define remote version
    use LWP::Simple;
    my $remote_version
        = get('https://raw.githubusercontent.com/qooob/authentic-theme/master/VERSION.txt');
    open( FILENAME, '<', \$remote_version );

    # Trim spaces
    $installed_version =~ s/\s+$//;
    $remote_version =~ s/\s+$//;

    # Parse response message
    if ( version->parse($remote_version)
        <= version->parse($installed_version) )
    {
        $authentic_theme_version
            = '<a href="https://github.com/qooob/authentic-theme" target="_blank">'
            . $text{'authentic_theme'} . '</a> '
            . $installed_version
            . '<div class="modal fade" id="update_notice" tabindex="-1" role="dialog" aria-labelledby="update_notice_label" aria-hidden="true">
                  <div class="modal-dialog">
                    <div class="modal-content">
                      <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>
                        <h4 class="modal-title" id="update_notice_label">'
            . $text{'theme_update_notice'} . '</h4>
                      </div>
                      <div class="modal-body">
                        <h4>Version 9.0.3 (February 3, 2015)</h4>
                        <ul>
                            <li>Fixed file selector <code>filter broken</code> in some cases <a href="https://github.com/qooob/authentic-theme/issues/81" target="_blank">(Issue 81)</a></li>
                            <li>Fixed a general bug (not theme related), when <code>clicking</code> on <em>external links</em> <a href="https://github.com/qooob/authentic-theme/issues/82" target="_blank">(Issue 82)</a></li>
                            <li>Fixed ConfigServer Security & Firewall <code>Firefox bug</code> when buttons didn\'t work <a href="https://github.com/qooob/authentic-theme/issues/83" target="_blank">(Issue 83)</a></li>
                        </ul>

                        <h4>Version 9.0.0-9.0.2 (February 1-2, 2015)</h4>
                        <ul>
                            <li>Fixed <code>loader</code> positioning</li>
                            <li>Fixed <code>small buttons</code> under the menu showing <em>correct language link</em> on toggling between <em>Webmin/Virtualmin/Cloudmin</em></li>
                            <li>Fixed <code>menu jumps</code> <a href="https://github.com/qooob/authentic-theme/issues/76" target="_blank">(Issue 76)</a></li>
                            <li>Fixed <code>selects</code> incorrectly triggering loader in some cases <a href="https://github.com/qooob/authentic-theme/issues/78" target="_blank">(Issue 78)</a></li>
                            <li>Improved <code>mobile menu</code> trigger button position and some other mobile menu tweaks</li>
                            <li>Fixed <code>Firefox bug</code> making right frame links not clickable <a href="https://github.com/qooob/authentic-theme/issues/74" target="_blank">(Issue 74)</a></li>
                            <li>Improved <code>navigation</code> menu auto-opening</li>
                            <li>Changed: Overall <code>UI redesign</code> for better experience</li>
                            <li>Changed: Code <code>core</code> complete rewrite for both <strong>server</strong> and <strong>client-side</strong>. Improved <code>speed</code> and <code>browser/plugin</code> compatibility</li>
                            <li>Added support for <strong>Virtualmin/Cloudmin</strong> <code>missing left menu</code>, for currently selected virtual server/machine. <strong><em>Attention:</em></strong> You need latest <strong>Virtualmin</strong> installation to make it work. (For <strong>Virtualmin</strong> <em>Pro</em>, minimum version requirement is 4.13 and for <em>GPL</em> users minimum is 4.14)</li>
                            <li>Added <code>autocomplete</code> for currently <code>opened module</code> in <strong>Webmin</strong>, currently <code>selected domain</code> and list of all available <code>virtual domains/machines</code> in <strong>Virtualmin/Cloudmin</strong> modules</li>
                            <li>Added <code>complete mobile support</code>. Navigation menu now has absolutely <strong>same functionality</strong> for both <strong>desktop/mobile</strong> versions</li>
                            <li>Added <code>custom logo</code> support. Manual for using it is on <a href="https://github.com/qooob/authentic-theme#how-do-i-set-custom-logo" target="_blank">GitHub</a> page</li>
                            <li>Added <code>screen-saver</code> effect (using pure CSS) after <strong>2 minutes</strong> of inactivity</li>
                            <li>Added <code>shortcut</code> <strong>Alt+R</strong> for <strong>reloading</strong> right frame</li>
                            <li>Added <code>Chinese translation</code> by <a href="https://github.com/Dreista" target="_blank">Dreista</a></li>
                        </ul>
                        <h4 style="margin-top:20px">'
            . $text{'theme_development_support'} . '</h4>
                        Thank you for using <a target="_blank" href="https://github.com/qooob/authentic-theme"><kbd style="background:#5cb85c">'
            . $text{'authentic_theme'}
            . '<kbd></a>. Overall development of this theme has already passed the stage of <kbd>200</kbd> hours.
                          While I am glad to provide <em>Authentic</em> Theme for free, it would mean a world to me, if you send me a <a target="_blank" class="badge fa fa-paypal" style="font-size: 11px; background-color: #5bc0de;" href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&lc=us&business=programming%40rostovtsev%2eru&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHostedGuest"> donation</a>.
                          It doesn\'t matter how big or small your donation is. I appreciate all donations. Each donation will excite future development and improve your everyday experience, while working with the theme.
                          <br>
                          <br>
                          Don\'t forget nor be lazy to post to <a class="badge fa fa-github" style="font-size: 11px; background-color: #337ab7;" target="_blank" href="https://github.com/qooob/authentic-theme"> GitHub</a> found bugs.<br>
                          <br>
                          Please rate/comment theme presentation on <a class="badge label-danger fa fa-youtube" style="font-size: 11px; background-color: #c9302c;" target="_blank" href="http://www.youtube.com/watch?v=gfuPFuGpyv8"> YouTube</a> channel.
                      </div>
                    </div>
                  </div>
               </div>';
    }
    else {
        $authentic_theme_version
            = '<a href="https://github.com/qooob/authentic-theme" target="_blank">'
            . $text{'authentic_theme'} . '</a> '
            . $installed_version . '. '
            . $text{'theme_update_available'} . ' '
            . $remote_version
            . '&nbsp;&nbsp;&nbsp;<div class="btn-group">'
            . '<a class="btn btn-xs btn-success authentic_update" style="padding:0 8px; height:21px" href="'
            . $gconfig{'webprefix'}
            . '/webmin/edit_themes.cgi"><i class="fa fa-refresh">&nbsp;</i>'
            . $text{'theme_update'} . '</a>'
            . '<a class="btn btn-xs btn-info" style="padding:0 8px; height:21px" target="_blank" href="https://github.com/qooob/authentic-theme/blob/master/CHANGELOG.md"><i class="fa fa-pencil-square-o">&nbsp;</i>'
            . $text{'theme_changelog'} . '</a>'
            . '<a class="btn btn-xs btn-default" style="padding:0 8px; height:21px" target="_blank" href="https://github.com/qooob/authentic-theme#donation"><i class="fa fa-rub">&nbsp;</i>'
            . $text{'theme_donate'} . '</a>'
            . '</div>';
    }
    &print_table_row( $text{'theme_version'}, $authentic_theme_version );

    #System Time
    $tm = localtime( time() );
    if ( &foreign_available("time") ) {
        $tm = '<a href=' . $gconfig{'webprefix'} . '/time/>' . $tm . '</a>';
    }
    &print_table_row( &text('body_time'), $tm );

    # Kernel and CPU Info
    if ( $info->{'kernel'} ) {
        &print_table_row(
            &text('body_kernel'),
            &text(
                'body_kernelon',                $info->{'kernel'}->{'os'},
                $info->{'kernel'}->{'version'}, $info->{'kernel'}->{'arch'}
            )
        );
    }

    # CPU Type and cores
    if ( $info->{'load'} ) {
        @c = @{ $info->{'load'} };
        if ( @c > 3 ) {
            &print_table_row( $text{'body_cpuinfo'},
                &text( 'body_cputype', @c ) );
        }
    }

    # Temperatures Info (if available)
    if ( $info->{'cputemps'} ) {
        foreach my $t ( @{ $info->{'cputemps'} } ) {
            $cputemp
                .= 'Core '
                . $t->{'core'} . ': '
                . int( $t->{'temp'} )
                . '&#176;C<br>';
        }
        &print_table_row( $text{'body_cputemps'}, $cputemp );
    }
    if ( $info->{'drivetemps'} ) {
        foreach my $t ( @{ $info->{'drivetemps'} } ) {
            my $short = $t->{'device'};
            $short =~ s/^\/dev\///;
            my $emsg;
            if ( $t->{'errors'} ) {
                $emsg
                    .= ' (<span class="text-danger">'
                    . &text( 'body_driveerr', $t->{'errors'} )
                    . "</span>)";
            }
            elsif ( $t->{'failed'} ) {
                $emsg
                    .= ' (<span class="text-danger">'
                    . &text('body_drivefailed')
                    . '</span>)';
            }
            $hddtemp
                .= $short . ': '
                . int( $t->{'temp'} )
                . '&#176;C<br>'
                . $emsg;
        }
        &print_table_row( $text{'body_drivetemps'}, $hddtemp );
    }

    # System uptime
    &foreign_require("proc");
    my $uptime;
    my ( $d, $h, $m ) = &proc::get_system_uptime();
    if ($d) {
        $uptime = &text( 'body_updays', $d, $h, $m );
    }
    elsif ($m) {
        $uptime = &text( 'body_uphours', $h, $m );
    }
    elsif ($m) {
        $uptime = &text( 'body_upmins', $m );
    }
    if ($uptime) {
        if ( &foreign_available("init") ) {
            $uptime
                = '<a href='
                . $gconfig{'webprefix'}
                . '/init/>'
                . $uptime . '</a>';
        }
        &print_table_row( $text{'body_uptime'}, $uptime );
    }

    # Running processes
    if ( &foreign_check("proc") ) {
        @procs = &proc::list_processes();
        $pr    = scalar(@procs);
        if ( &foreign_available("proc") ) {
            $pr
                = '<a href='
                . $gconfig{'webprefix'}
                . '/proc/>'
                . $pr . '</a>';
        }
        &print_table_row( $text{'body_procs'}, $pr );
    }

    # Load averages
    if ( $info->{'load'} ) {
        @c = @{ $info->{'load'} };
        if (@c) {
            &print_table_row( $text{'body_cpu'}, &text( 'body_load', @c ) );
        }
    }

    # Real memory details
    &print_table_row(
        $text{'body_real'},
        &text(
            'body_used',
            nice_size( ( $m[0] ) * 1000 ),
            nice_size( ( $m[0] - $m[1] ) * 1000 )
        )
    );

    # Virtual memory details
    &print_table_row(
        $text{'body_virt'},
        &text(
            'body_used',
            nice_size( ( $m[2] ) * 1000 ),
            nice_size( ( $m[2] - $m[3] ) * 1000 )
        )
    );

    # Local disk space
    &print_table_row(
        $text{'body_disk'},
        &text(
            'body_used_and_free',
            nice_size( $info->{'disk_total'} ),
            nice_size( $info->{'disk_free'} ),
            nice_size( $info->{'disk_total'} - $info->{'disk_free'} )
        )
    );

    # Package updates
    if ( $info->{'poss'} ) {
        @poss = @{ $info->{'poss'} };
        @secs = grep { $_->{'security'} } @poss;
        if ( @poss && @secs ) {
            $msg = &text( 'body_upsec', scalar(@poss), scalar(@secs) );
        }
        elsif (@poss) {
            $msg = &text( 'body_upneed', scalar(@poss) );
        }
        else {
            $msg = $text{'body_upok'};
        }
        if ( &foreign_available("package-updates") ) {
            $msg
                = '<a href="'
                . $gconfig{'webprefix'}
                . '/package-updates/index.cgi?mode=updates">'
                . $msg
                . '</a> <a href="/?updated" target="_top" data-href="'
                . $gconfig{'webprefix'}
                . '/webmin/edit_webmincron.cgi" data-refresh="system-status package-updates" class="btn btn-primary btn-xs btn-hidden hidden" style="margin-left:4px;color: white;padding:0 12px; line-height: 12px; height:15px; font-size:11px"><i class="fa fa-refresh"></i></a>';
        }
        &print_table_row( $text{'body_updates'}, $msg );
    }
    print '</table>' . "\n";

    # Webmin notifications
    print '</div>' . "\n";
    if ( &foreign_check("webmin") ) {
        &foreign_require( "webmin", "webmin-lib.pl" );
        my @notifs = &webmin::get_webmin_notifications();
        if (@notifs) {
            print '<div class="panel-footer">' . "\n";
            print "<center>\n", join( "<hr>\n", @notifs ), "</center>\n";
            print '</div>' . "\n";
        }

        # print scalar(@notifs);
    }
}
elsif ( $level == 2 ) {

    # Domain owner
    # Show a server owner info about one domain
    $ex = virtual_server::extra_admin();
    if ($ex) {
        $d = virtual_server::get_domain($ex);
    }
    else {
        $d = virtual_server::get_domain_by( "user", $remote_user, "parent",
            "" );
    }

    print '<table class="table table-hover">' . "\n";

    &print_table_row( $text{'right_login'}, $remote_user );

    &print_table_row( $text{'right_from'}, $ENV{'REMOTE_HOST'} );

    if ($hasvirt) {
        &print_table_row( $text{'right_virtualmin'},
            $virtual_server::module_info{'version'} );
    }
    else {
        &print_table_row( $text{'right_virtualmin'}, $text{'right_not'} );
    }

    $dname
        = defined(&virtual_server::show_domain_name)
        ? &virtual_server::show_domain_name($d)
        : $d->{'dom'};
    &print_table_row( $text{'right_dom'}, $dname );

    @subs = ( $d, virtual_server::get_domain_by( "parent", $d->{'id'} ) );
    @reals = grep { !$_->{'alias'} } @subs;
    @mails = grep { $_->{'mail'} } @subs;
    ( $sleft, $sreason, $stotal, $shide )
        = virtual_server::count_domains("realdoms");
    if ( $sleft < 0 || $shide ) {
        &print_table_row( $text{'right_subs'}, scalar(@reals) );
    }
    else {
        &print_table_row( $text{'right_subs'},
            text( 'right_of', scalar(@reals), $stotal ) );
    }

    @aliases = grep { $_->{'alias'} } @subs;
    if (@aliases) {
        ( $aleft, $areason, $atotal, $ahide )
            = virtual_server::count_domains("aliasdoms");
        if ( $aleft < 0 || $ahide ) {
            &print_table_row( $text{'right_aliases'}, scalar(@aliases) );
        }
        else {
            &print_table_row( $text{'right_aliases'},
                text( 'right_of', scalar(@aliases), $atotal ) );
        }
    }

    # Users and aliases info
    $users = virtual_server::count_domain_feature( "mailboxes", @subs );
    ( $uleft, $ureason, $utotal, $uhide )
        = virtual_server::count_feature("mailboxes");
    $msg = @mails ? $text{'right_fusers'} : $text{'right_fusers2'};
    if ( $uleft < 0 || $uhide ) {
        &print_table_row( $msg, $users );
    }
    else {
        &print_table_row( $msg, text( 'right_of', $users, $utotal ) );
    }

    if (@mails) {
        $aliases = virtual_server::count_domain_feature( "aliases", @subs );
        ( $aleft, $areason, $atotal, $ahide )
            = virtual_server::count_feature("aliases");
        if ( $aleft < 0 || $ahide ) {
            &print_table_row( $text{'right_faliases'}, $aliases );
        }
        else {
            &print_table_row( $text{'right_faliases'},
                text( 'right_of', $aliases, $atotal ) );
        }
    }

    # Databases
    $dbs = virtual_server::count_domain_feature( "dbs", @subs );
    ( $dleft, $dreason, $dtotal, $dhide )
        = virtual_server::count_feature("dbs");
    if ( $dleft < 0 || $dhide ) {
        &print_table_row( $text{'right_fdbs'}, $dbs );
    }
    else {
        &print_table_row( $text{'right_fdbs'},
            text( 'right_of', $dbs, $dtotal ) );
    }

    if ( !$sects->{'noquotas'}
        && virtual_server::has_home_quotas() )
    {
        # Disk usage for all owned domains
        $homesize = virtual_server::quota_bsize("home");
        $mailsize = virtual_server::quota_bsize("mail");
        ( $home, $mail, $db ) = virtual_server::get_domain_quota( $d, 1 );
        $usage = $home * $homesize + $mail * $mailsize + $db;
        $limit = $d->{'quota'} * $homesize;
        if ($limit) {
            &print_table_row( $text{'right_quota'},
                text( 'right_of', nice_size($usage), &nice_size($limit) ),
                3 );
        }
        else {
            &print_table_row( $text{'right_quota'}, nice_size($usage), 3 );
        }
    }

    if (  !$sects->{'nobw'}
        && $virtual_server::config{'bw_active'}
        && $d->{'bw_limit'} )
    {
        # Bandwidth usage and limit
        &print_table_row(
            $text{'right_bw'},
            &text(
                'right_of',
                &nice_size( $d->{'bw_usage'} ),
                &text(
                    'edit_bwpast_' . $virtual_server::config{'bw_past'},
                    &nice_size( $d->{'bw_limit'} ),
                    $virtual_server::config{'bw_period'}
                )
            ),
            3
        );
    }

    print '</table>' . "\n";

    # New features for domain owner
    show_new_features(0);
}
elsif ( $level == 3 ) {
    print '<table class="table table-hover">' . "\n";

    # Host and login info
    &print_table_row( &text('body_host'), &get_system_hostname() );

    # Operating System Info
    if ( $gconfig{'os_version'} eq '*' ) {
        $os = $gconfig{'real_os_type'};
    }
    else {
        $os = $gconfig{'real_os_type'} . ' ' . $gconfig{'real_os_version'};
    }
    &print_table_row( &text('body_os'), $os );

    # Usermin version
    &print_table_row( &text('body_usermin'), &get_webmin_version() );

    # Theme version/updates
    # Define installed version
    open my $authentic_installed_version, '<',
        $root_directory . "/authentic-theme/VERSION.txt";
    my $installed_version = <$authentic_installed_version>;
    close $authentic_installed_version;

    # Define remote version
    use LWP::Simple;
    my $remote_version
        = get('https://raw.githubusercontent.com/qooob/authentic-theme/master/VERSION.txt');
    open( FILENAME, '<', \$remote_version );

    # Trim spaces
    $installed_version =~ s/\s+$//;
    $remote_version =~ s/\s+$//;

    # Parse response message
    if ( version->parse($remote_version)
        <= version->parse($installed_version) )
    {
        $authentic_theme_version
            = '' . $text{'authentic_theme'} . ' ' . $installed_version;
    }
    else {
        $authentic_theme_version
            = ''
            . $text{'authentic_theme'} . ' '
            . $installed_version . '. '
            . $text{'theme_update_available'} . ' '
            . $remote_version
            . '&nbsp;&nbsp;<a class="btn btn-xs btn-info" style="padding:0 8px; height:21px" target="_blank" href="https://github.com/qooob/authentic-theme/blob/master/CHANGELOG.md">'
            . ''
            . $text{'theme_changelog'} . '</a>';
    }
    &print_table_row( $text{'theme_version'}, $authentic_theme_version );

    #System Time
    $tm = localtime( time() );
    if ( &foreign_available("time") ) {
        $tm = '<a href=' . $gconfig{'webprefix'} . '/time/>' . $tm . '</a>';
    }
    &print_table_row( &text('body_time'), $tm );

    # Disk quotas
    if ( &foreign_installed("quota") ) {
        &foreign_require( "quota", "quota-lib.pl" );
        $n     = &quota::user_filesystems($remote_user);
        $usage = 0;
        $quota = 0;
        for ( $i = 0; $i < $n; $i++ ) {
            if ( $quota::filesys{ $i, 'hblocks' } ) {
                $quota += $quota::filesys{ $i, 'hblocks' };
                $usage += $quota::filesys{ $i, 'ublocks' };
            }
            elsif ( $quota::filesys{ $i, 'sblocks' } ) {
                $quota += $quota::filesys{ $i, 'sblocks' };
                $usage += $quota::filesys{ $i, 'ublocks' };
            }
        }
        if ($quota) {
            $bsize = $quota::config{'block_size'};
            print '<tr>' . "\n";
            print '<td><strong>'
                . $text{'body_uquota'}
                . '</strong></td>' . "\n";
            print '<td>'
                . &text(
                'right_out',
                &nice_size( $usage * $bsize ),
                &nice_size( $quota * $bsize )
                ),
                '</td>' . "\n";
            print '</tr>' . "\n";
            print '<tr>' . "\n";
            print '<td></td>' . "\n";
            print '<td>' . "\n";
            print '<div class="progress">' . "\n";
            $used = $usage / $quota * 100;
            print
                '<div class="progress-bar progress-bar-info" role="progressbar" aria-valuenow="'
                . $used
                . '" aria-valuemin="0" aria-valuemax="100" style="width: '
                . $used . '%">' . "\n";
            print '</div>' . "\n";
            print '</div>' . "\n";
            print '</td>' . "\n";
            print '</tr>' . "\n";
        }
    }
    print '</table>' . "\n";
}

# End of page
print '</div>' . "\n";
print '</div>' . "\n";
print '</div>' . "\n";

&footer();
