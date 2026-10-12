import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_hbb/common/glass.dart';
import 'package:flutter_test/flutter_test.dart';

Future<void> _fonts() async {
  Future<ByteData> f(String p) => Future.value(ByteData.sublistView(File(p).readAsBytesSync()));
  final text = FontLoader('DejaVu')
    ..addFont(f('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    ..addFont(f('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'));
  await text.load();
  final icons = FontLoader('MaterialIcons')
    ..addFont(f('/tmp/claude-0/flutter-sdk/bin/cache/artifacts/material_fonts/MaterialIcons-Regular.otf'));
  await icons.load();
}

ThemeData _theme(bool dark) {
  final b = dark ? ThemeData.dark() : ThemeData.light();
  return glassifyTheme(b.copyWith(
    colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF5CB888),
        brightness: dark ? Brightness.dark : Brightness.light),
    textTheme: b.textTheme.apply(fontFamily: 'DejaVu'),
    iconTheme: IconThemeData(color: dark ? Colors.white70 : Colors.black54),
  ));
}

Widget _wrapPlain(Widget home, bool dark) => MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: _theme(dark),
      home: Material(color: Colors.transparent, child: home),
    );

Widget _wrap(Widget home, bool dark) => MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: _theme(dark),
      builder: (c, child) => glassWrap(c, child),
      home: home,
    );

const _accent = Color(0xFF5CB888);

// ---------------------------------------------------------------- Android
Widget _android(bool dark) {
  return Builder(builder: (context) {
    Widget peer(String name, String id, IconData ic) => glassCard(context,
        margin: const EdgeInsets.symmetric(horizontal: 14),
        child: ListTile(
          leading: CircleAvatar(
              backgroundColor: _accent,
              child: Icon(ic, color: Colors.white, size: 20)),
          title: Text(name),
          subtitle: Text(id),
          trailing: const Icon(Icons.more_vert),
        ));
    return Scaffold(
      extendBody: true,
      appBar: AppBar(
        centerTitle: true,
        title: const Text('AlphaLink'),
        actions: const [Icon(Icons.search), SizedBox(width: 12), Icon(Icons.more_vert), SizedBox(width: 8)],
      ),
      body: ListView(children: [
        const SizedBox(height: 6),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: Glass(
            radius: 24,
            padding: const EdgeInsets.fromLTRB(18, 16, 18, 16),
            child: Row(children: [
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: const [
                  Text('Your ID', style: TextStyle(fontSize: 12)),
                  SizedBox(height: 4),
                  Text('482 917 305', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
                ]),
              ),
              const Icon(Icons.qr_code_2, size: 34),
            ]),
          ),
        ),
        const SizedBox(height: 10),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: Glass(
            radius: 26,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: const TextField(
              decoration: InputDecoration(
                  border: InputBorder.none,
                  hintText: 'Enter remote ID',
                  suffixIcon: Icon(Icons.arrow_forward)),
            ),
          ),
        ),
        const SizedBox(height: 6),
        peer('Office-PC', '112 334 556', Icons.window),
        peer('Home Mac mini', '908 771 204', Icons.laptop_mac),
        peer('Pixel tablet', '305 642 118', Icons.tablet_android),
        peer('Server room', '771 090 433', Icons.dns),
        peer('Laptop', '640 118 902', Icons.laptop),
      ]),
      bottomNavigationBar: glassBottomBar(
          context,
          BottomNavigationBar(
            backgroundColor: Colors.transparent,
            elevation: 0,
            type: BottomNavigationBarType.fixed,
            selectedItemColor: _accent,
            unselectedItemColor: dark ? Colors.white60 : Colors.black45,
            currentIndex: 0,
            items: const [
              BottomNavigationBarItem(icon: Icon(Icons.devices), label: 'Connect'),
              BottomNavigationBarItem(icon: Icon(Icons.chat_bubble_outline), label: 'Chat'),
              BottomNavigationBarItem(icon: Icon(Icons.cast), label: 'Share'),
              BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'Settings'),
            ],
          )),
    );
  });
}

Widget _statusBar(bool dark) => Padding(
      padding: const EdgeInsets.fromLTRB(22, 10, 22, 0),
      child: Row(children: [
        Text('12:30', style: TextStyle(fontFamily: 'DejaVu', fontSize: 13, fontWeight: FontWeight.bold, color: dark ? Colors.white : Colors.black87)),
        const Spacer(),
        Icon(Icons.wifi, size: 15, color: dark ? Colors.white : Colors.black87),
        const SizedBox(width: 6),
        Icon(Icons.signal_cellular_alt, size: 15, color: dark ? Colors.white : Colors.black87),
        const SizedBox(width: 6),
        Icon(Icons.battery_full, size: 15, color: dark ? Colors.white : Colors.black87),
      ]),
    );

// ---------------------------------------------------------------- macOS
Widget _mac(bool dark) {
  return Builder(builder: (context) {
    final txt = dark ? Colors.white : Colors.black87;
    Widget chip(String t, bool sel) => Container(
          margin: const EdgeInsets.only(right: 8),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
          decoration: BoxDecoration(
            color: sel ? _accent.withOpacity(0.85) : glassSurfaceColor(context),
            borderRadius: BorderRadius.circular(18),
          ),
          child: Text(t, style: TextStyle(fontSize: 13, color: sel ? Colors.white : txt)),
        );
    Widget card(String name, String id, IconData ic, Color head) => Glass(
          radius: 16,
          blur: 16,
          shadow: false,
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Container(
              height: 78,
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: [head.withOpacity(0.85), head.withOpacity(0.45)]),
              ),
              child: Center(child: Icon(ic, size: 40, color: Colors.white)),
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Row(children: [
                Container(width: 9, height: 9, decoration: const BoxDecoration(color: _accent, shape: BoxShape.circle)),
                const SizedBox(width: 8),
                Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(name, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                  Text(id, style: const TextStyle(fontSize: 11)),
                ])),
                const Icon(Icons.more_vert, size: 18),
              ]),
            ),
          ]),
        );
    final cards = [
      card('Office-PC', '112 334 556', Icons.window, const Color(0xFF2F6BFF)),
      card('Home Mac mini', '908 771 204', Icons.laptop_mac, const Color(0xFF8E8E93)),
      card('Server room', '771 090 433', Icons.dns, const Color(0xFFE5883B)),
      card('Ubuntu box', '305 642 118', Icons.computer, const Color(0xFFE95420)),
      card('Pixel tablet', '640 118 902', Icons.tablet_android, const Color(0xFF3DDC84)),
      card('Laptop', '233 019 777', Icons.laptop, const Color(0xFF7B61FF)),
    ];
    return Scaffold(
      body: Column(children: [
        // title bar
        Container(
          height: 38,
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: Row(children: [
            for (final c in const [Color(0xFFFF5F57), Color(0xFFFEBC2E), Color(0xFF28C840)])
              Container(margin: const EdgeInsets.only(right: 8), width: 12, height: 12, decoration: BoxDecoration(color: c, shape: BoxShape.circle)),
            Expanded(child: Center(child: Text('AlphaLink', style: TextStyle(fontSize: 13, color: txt.withOpacity(0.8))))),
            const SizedBox(width: 60),
          ]),
        ),
        Expanded(
          child: Row(children: [
            GlassPane(
              width: 230,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(18, 18, 18, 12),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  const Text('Your Desktop', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  const Text('Your desktop can be accessed with this ID and password.', style: TextStyle(fontSize: 11)),
                  const SizedBox(height: 18),
                  const Text('ID', style: TextStyle(fontSize: 11)),
                  const Text('482 917 305', style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 14),
                  const Text('One-time password', style: TextStyle(fontSize: 11)),
                  Row(children: const [
                    Text('7k3Qp9aX', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    Spacer(),
                    Icon(Icons.refresh, size: 18),
                  ]),
                  const Spacer(),
                  Row(children: [
                    Container(width: 9, height: 9, decoration: const BoxDecoration(color: _accent, shape: BoxShape.circle)),
                    const SizedBox(width: 8),
                    const Text('Ready', style: TextStyle(fontSize: 12)),
                    const Spacer(),
                    const Icon(Icons.settings, size: 18),
                  ]),
                ]),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(22, 14, 22, 18),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Glass(
                    radius: 14,
                    blur: 18,
                    shadow: false,
                    padding: const EdgeInsets.symmetric(horizontal: 14),
                    child: const SizedBox(
                      height: 42,
                      child: Row(children: [
                        Icon(Icons.search, size: 18),
                        SizedBox(width: 10),
                        Expanded(child: Text('Enter remote ID', style: TextStyle(fontSize: 13))),
                        Icon(Icons.arrow_forward, size: 18),
                      ]),
                    ),
                  ),
                  const SizedBox(height: 14),
                  Row(children: [chip('Recent', true), chip('Favorites', false), chip('Discovered', false), chip('Address Book', false)]),
                  const SizedBox(height: 14),
                  Expanded(
                    child: GridView.count(
                      crossAxisCount: 3,
                      mainAxisSpacing: 14,
                      crossAxisSpacing: 14,
                      childAspectRatio: 1.55,
                      children: cards,
                    ),
                  ),
                ]),
              ),
            ),
          ]),
        ),
      ]),
    );
  });
}

Widget _phoneFrame(Widget app, bool dark) => Container(
      color: dark ? const Color(0xFF1B1B1F) : const Color(0xFFD9DDE3),
      child: Center(
        child: Container(
          width: 400,
          height: 860,
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(color: Colors.black, borderRadius: BorderRadius.circular(46)),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(38),
            child: Stack(children: [
              Padding(padding: const EdgeInsets.only(top: 26), child: GlassBackground(child: app)),
              Positioned(top: 0, left: 0, right: 0, child: Material(type: MaterialType.transparency, child: _statusBar(dark))),
              Positioned(
                bottom: 6,
                left: 130,
                right: 130,
                height: 4,
                child: DecoratedBox(decoration: BoxDecoration(color: dark ? Colors.white54 : Colors.black45, borderRadius: BorderRadius.circular(2))),
              ),
            ]),
          ),
        ),
      ),
    );

Widget _macFrame(Widget app) => Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF4B3A8C), Color(0xFF2B5FA8), Color(0xFFD27AA0)],
        ),
      ),
      child: Center(
        child: Container(
          width: 1100,
          height: 700,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(14),
            boxShadow: const [BoxShadow(color: Color(0x88000000), blurRadius: 40, offset: Offset(0, 18))],
          ),
          child: ClipRRect(borderRadius: BorderRadius.circular(14), child: app),
        ),
      ),
    );

void main() {
  testWidgets('platform previews', (tester) async {
    await _fonts();
    Future<void> shot(Widget w, Size logical, String name) async {
      tester.view.physicalSize = logical * 2;
      tester.view.devicePixelRatio = 2.0;
      await tester.pumpWidget(w);
      await tester.pumpAndSettle();
      await expectLater(find.byType(MaterialApp), matchesGoldenFile('goldens/$name.png'));
    }

    addTearDown(tester.view.reset);
    for (final dark in [true, false]) {
      await shot(_wrapPlain(_phoneFrame(Builder(builder: (c) => _android(dark)), dark), dark), const Size(430, 920), 'android_${dark ? 'dark' : 'light'}');
      await shot(_wrap(_macFrame(_mac(dark)), dark), const Size(1280, 780), 'macos_${dark ? 'dark' : 'light'}');
    }
  });
}
