import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_hbb/common/glass.dart';
import 'package:flutter_test/flutter_test.dart';

Future<void> _font() async {
  final loader = FontLoader('DejaVu');
  loader.addFont(Future.value(
      ByteData.sublistView(File('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf').readAsBytesSync())));
  loader.addFont(Future.value(
      ByteData.sublistView(File('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf').readAsBytesSync())));
  await loader.load();
}

Widget _app(Widget home, {bool dark = true}) {
  final base = (dark ? ThemeData.dark() : ThemeData.light()).copyWith(
    primaryColor: const Color(0xFF5CB888),
    colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF5CB888),
        brightness: dark ? Brightness.dark : Brightness.light),
    textTheme: (dark ? ThemeData.dark() : ThemeData.light())
        .textTheme
        .apply(fontFamily: 'DejaVu'),
  );
  return MaterialApp(
    debugShowCheckedModeBanner: false,
    theme: glassifyTheme(base),
    builder: (c, child) => glassWrap(c, child),
    home: home,
  );
}


void main() {
  testWidgets('glass preview', (tester) async {
    await _font();
    tester.view.physicalSize = const Size(780, 1688);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(tester.view.reset);

    for (final dark in [true, false]) {
      await tester.pumpWidget(_app(
        Builder(builder: (context) {
          Widget peer(String name, String id) => glassCard(context,
              margin: const EdgeInsets.symmetric(horizontal: 12),
              child: ListTile(
                leading: CircleAvatar(
                    backgroundColor: const Color(0xFF5CB888),
                    child: Text(name[0])),
                title: Text(name),
                subtitle: Text(id),
                trailing: const Icon(Icons.more_vert),
              ));
          return Scaffold(
            extendBody: true,
            appBar: AppBar(centerTitle: true, title: const Text('AlphaLink')),
            body: ListView(children: [
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: Glass(
                  radius: 22,
                  padding: const EdgeInsets.all(16),
                  child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: const [
                        Text('Your ID', style: TextStyle(fontSize: 13)),
                        SizedBox(height: 6),
                        Text('482 917 305',
                            style: TextStyle(
                                fontSize: 30, fontWeight: FontWeight.bold)),
                      ]),
                ),
              ),
              const SizedBox(height: 12),
              peer('Office-PC', '112 334 556'),
              peer('Home Mac mini', '908 771 204'),
              peer('Laptop', '305 642 118'),
              peer('Server room', '771 090 433'),
            ]),
            bottomNavigationBar: glassBottomBar(
                context,
                BottomNavigationBar(
                  backgroundColor: Colors.transparent,
                  elevation: 0,
                  type: BottomNavigationBarType.fixed,
                  selectedItemColor: const Color(0xFF5CB888),
                  currentIndex: 0,
                  items: const [
                    BottomNavigationBarItem(icon: Icon(Icons.devices), label: 'Connect'),
                    BottomNavigationBarItem(icon: Icon(Icons.chat), label: 'Chat'),
                    BottomNavigationBarItem(icon: Icon(Icons.screen_share), label: 'Share'),
                    BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'Settings'),
                  ],
                )),
          );
        }),
        dark: dark,
      ));
      await tester.pumpAndSettle();
      await expectLater(find.byType(MaterialApp),
          matchesGoldenFile('goldens/home_${dark ? 'dark' : 'light'}.png'));
    }

    await tester.pumpWidget(_app(
      Scaffold(
        body: Center(
          child: GlassDialog(
            title: const Text('Connection Error'),
            titlePadding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
            content: const Text('Failed to connect to rendezvous server. Retrying...'),
            contentPadding: const EdgeInsets.fromLTRB(24, 16, 24, 8),
            actions: [
              TextButton(onPressed: () {}, child: const Text('Cancel')),
              TextButton(onPressed: () {}, child: const Text('Reconnect')),
            ],
            actionsPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            buttonSpacing: 8,
          ),
        ),
      ),
    ));
    await tester.pumpAndSettle();
    await expectLater(find.byType(MaterialApp), matchesGoldenFile('goldens/dialog_dark.png'));
  });
}
