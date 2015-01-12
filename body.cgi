#
# Authentic Theme 8.1.0 (https://github.com/qooob/authentic-theme)
# Copyright 2015 Ilia Rostovtsev <programming@rostovtsev.ru>
# Licensed under MIT (https://github.com/qooob/authentic-theme/blob/master/LICENSE)
#

BEGIN { push( @INC, ".." ); }
use WebminCore;
&ReadParse();
&init_config();
&load_theme_library();
use Time::Local;
( $hasvirt, $level, $hasvm2 ) = get_virtualmin_user_level();
%text = &load_language($current_theme);
%text = ( &load_language('virtual-server'), %text );

if ( $hasvirt && $in{'dom'} ) {
    $defdom = virtual_server::get_domain( $in{'dom'} );
}

&header($title);
print '<div id="wrapper" class="page" data-notice="'
    . (( -f $root_directory . '/authentic-theme/update' ) ? do { '1'; unlink $root_directory . '/authentic-theme/update'; } : 0) . '">' . "\n";
print '<div class="container">' . "\n";
print '<div id="system-status" class="panel panel-default">' . "\n";
print '<div class="panel-heading">' . "\n";
print '<h3 class="panel-title">' . &text('body_header0') . (
    ( $level != 2 && $level != 3 )
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
                        <h4>Version 8.1.0 (January 9, 2015)</h4>
                        <ul>
                            <li>Fixed script removing <em>text</em> in rare cases, next to <code>radios/checkboxes</code>, which is actually crucial for understanding of what to select</li>
                            <li>Changed alien Alt sign <code>⌥</code> to <code>Alt</code>, which now also only appears <code>onfocus</code> on search field (thanks to <em>Joe Cooper</em> for advice)</li>
                            <li>Fixed <em>dozens</em> of UI issues, like broken borders on tables and some other visual improvements (now theme provides most accurate UI <em>ever</em> achieved)</li>
                            <li>Removed donation button from <em>System Information</em> page, that was seen on everyday basis (thanks to <em>Joe Cooper</em> for advice)</li>
                        </ul>
                        <h4 style="margin-top:20px">'
            . $text{'theme_development_support'} . '</h4>
                        Thank you for using <a target="_blank" href="https://github.com/qooob/authentic-theme"><kbd style="background:#5cb85c">'
            . $text{'authentic_theme'}
            . '<kbd></a>. Overall development of this theme has already passed the stage of 100 hours.
                          While I am happy to provide <em>Authentic Theme</em> for free, it would mean very much to me, if you could send me a <a target="_blank" href="https://github.com/qooob/authentic-theme#donation">donation</a>.
                          It doesn\'t matter how big or small your donation is. I appreciate all donations. Each donation will excite future development.
                          <br>
                          <br>
                          Don\'t forget nor be lazy to post to <a class="label label-primary fa fa-github" style="font-size: 11px" target="_blank" href="https://github.com/qooob/authentic-theme"> GitHub</a> found issues.
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

sub print_progressbar_colum {
    my ( $xs, $sm, $percent, $label ) = @_;
    use POSIX;
    $percent = ceil($percent);
    if ( $percent < 75 ) {
        $class = 'success';
    }
    elsif ( $percent < 90 ) {
        $class = 'warning';
    }
    else {
        $class = 'danger';
    }
    print '<div class="col-xs-' . $xs . ' col-sm-' . $sm . '">' . "\n";
    print '<div data-progress="'
        . $percent
        . '" class="progress progress-circle">' . "\n";
    print '<div class="progress-bar-circle progress-bar-' . $class . '">'
        . "\n";
    print '<div class="progress-bar-circle-mask progress-bar-circle-full">'
        . "\n";
    print '<div class="progress-bar-circle-fill"></div>' . "\n";
    print '</div>' . "\n";
    print '<div class="progress-bar-circle-mask progress-bar-circle-half">'
        . "\n";
    print '<div class="progress-bar-circle-fill"></div>' . "\n";
    print
        '<div class="progress-bar-circle-fill progress-bar-circle-fix"></div>'
        . "\n";
    print '</div>' . "\n";
    print '<div class="progress-bar-circle-inset">' . "\n";
    print '<div class="progress-bar-circle-title">' . "\n";
    print '<strong class="text-muted">' . $label . '</strong>' . "\n";
    print '</div>' . "\n";
    print '<div class="progress-bar-circle-percent">' . "\n";
    print '<span></span>' . "\n";
    print '</div>' . "\n";
    print '</div>' . "\n";
    print '</div>' . "\n";
    print '</div>' . "\n";
    print '</div>' . "\n";
}

sub get_col_num {
    my ( $info, $max_col ) = @_;
    my $num_col = 0;
    if ( $info->{'cpu'} ) { $num_col++; }
    if ( $info->{'mem'} ) {
        @m = @{ $info->{'mem'} };
        if ( @m && $m[0] ) { $num_col++; }
        if ( @m && $m[2] ) { $num_col++; }
    }
    if ( $info->{'disk_total'} ) { $num_col++; }
    my $col = $max_col / $num_col;
    return $col;
}

sub print_table_row {
    local ( $title, $content ) = @_;
    print '<tr>' . "\n";
    print '<td style="vertical-align:middle; padding:10px;"><strong>'
        . $title
        . '</strong></td>' . "\n";
    print '<td  style="vertical-align:middle; padding:10px;">'
        . $content . '</td>' . "\n";
    print '</tr>' . "\n";
}

sub get_virtualmin_user_level {
    local ( $hasvirt, $hasvm2, $level );
    $hasvm2  = &foreign_available("server-manager");
    $hasvirt = &foreign_available("virtual-server");
    if ($hasvm2) {
        &foreign_require( "server-manager", "server-manager-lib.pl" );
    }
    if ($hasvirt) {
        &foreign_require( "virtual-server", "virtual-server-lib.pl" );
    }
    if ($hasvm2) {
        $level = $server_manager::access{'owner'} ? 4 : 0;
    }
    elsif ($hasvirt) {
        $level
            = &virtual_server::master_admin()   ? 0
            : &virtual_server::reseller_admin() ? 1
            :                                     2;
    }
    elsif ( &get_product_name() eq "usermin" ) {
        $level = 3;
    }
    else {
        $level = 0;
    }
    return ( $hasvirt, $level, $hasvm2 );
}

sub show_new_features {
    my ($nosect) = @_;
    my $newhtml;
    if (   $hasvirt
        && !$sects->{'nonewfeatures'}
        && defined(&virtual_server::get_new_features_html)
        && ( $newhtml = virtual_server::get_new_features_html($defdom) ) )
    {
        # Show new features HTML for Virtualmin
        if ($nosect) {
            print "<h3>$text{'right_newfeaturesheader'}</h3>\n";
        }
        else {
            print ui_hidden_table_start( $text{'right_newfeaturesheader'},
                "width=100%", 2, "newfeatures", 1 );
        }
        print &ui_table_row( undef, $newhtml, 2 );
        if ( !$nosect ) {
            print ui_hidden_table_end("newfeatures");
        }
    }
    if (   $hasvm2
        && !$sects->{'nonewfeatures'}
        && defined(&server_manager::get_new_features_html)
        && ( $newhtml = server_manager::get_new_features_html(undef) ) )
    {
        # Show new features HTML for Cloudmin
        if ($nosect) {
            print "<h3>$text{'right_newfeaturesheadervm2'}</h3>\n";
        }
        else {
            print ui_hidden_table_start( $text{'right_newfeaturesheadervm2'},
                "width=100%", 2, "newfeaturesvm2", 1 );
        }
        print &ui_table_row( undef, $newhtml, 2 );
        if ( !$nosect ) {
            print ui_hidden_table_end("newfeaturesvm2");
        }
    }
}

sub parse_license_date {
    if ( $_[0] =~ /^(\d{4})-(\d+)-(\d+)$/ ) {
        return eval { timelocal( 0, 0, 0, $3, $2 - 1, $1 - 1900 ) };
    }
    return undef;
}
