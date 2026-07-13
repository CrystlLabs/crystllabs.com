---
title: The 80MB "Hello World": Why Your Framework Is a Liability
date: 2026-07-13
summary: A fresh React Native "Hello, World" ships 50-80MB of native libraries and boots an entire second runtime before it draws a pixel; the same app in native Kotlin lands under 500KB. Binary size and boot latency aren't implementation details, they're user-facing costs paid on every install and every cold start.
tags: Architecture, Native, Performance
---

Everyone in this industry loves to talk about shipping fast. Sprint velocity. CI/CD pipelines. Hot reload. The whole vocabulary is built around speed as a virtue. But there's a second kind of speed nobody in a standup ever mentions: the four seconds your user spends staring at a blank splash screen while your "fast" app boots up. That silence is where your framework quietly picks their pocket.

Let's do something almost nobody actually does before adopting a framework. Let's open the box.

## The Experiment

Take the most vanilla possible starting point: a fresh React Native project, npx react-native init HelloWorld, zero business logic, one Text component that says "Hello, World." Build a release APK. Run unzip -l on it, or better, pull it apart with bundletool and look at what's actually inside.

You will find, conservatively, somewhere in the neighborhood of 20 to 25MB for a single-architecture release build, and closer to 50-80MB once you account for a universal APK bundling armeabi-v7a, arm64-v8a, x86, and x86_64 native libraries side by side, because your app doesn't know in advance which chip it's landing on. Do the same exercise with Flutter and you'll find a broadly similar story: a libflutter.so weighing in around 6-8MB per architecture before your code has drawn a single pixel of your actual UI.

Now open one of those .so files in a disassembler, or just run nm and grep for symbol counts. You are not looking at your app. You are looking at an entire second operating system that got smuggled into your app's skeleton: a JavaScript engine (Hermes or JavaScriptCore), a Skia rendering pipeline, a full bridge/JSI layer for shuttling data between native and JS threads, a reconciler that diffs virtual trees sixty times a second whether you need it to or not, and a dependency graph in node_modules that, by the time you've added three UI libraries and a state manager, comfortably exceeds 500MB of source before tree-shaking even gets a chance to fight back.

Your "Hello World" is booting an interpreter. It is initializing a garbage collector. It is standing up a bridge between two runtimes so that eventually, someday, you might want to call fetch(). None of that infrastructure printed a single letter of "Hello." It just made sure the letters could be printed, at the cost of a boot sequence your user has to sit through every cold start.

## Where the Weight Actually Comes From

It's worth being precise here, because "frameworks are bloated" is a lazy accusation unless you can point at the line items.

**The runtime tax.** React Native ships a JS engine inside your binary because Android doesn't have one it can lend you (this changes slightly with Hermes bytecode precompilation, but the engine itself is still along for the ride). Flutter ships its own rendering engine, Skia, rather than using platform-native views, because cross-platform pixel parity matters more to the framework's value proposition than binary size does. Both of these are rational engineering tradeoffs from the framework author's perspective. They are also fixed costs you pay before writing a single feature.

**The abstraction tax.** Every cross-platform framework's entire pitch is "write once, run anywhere," which mechanically requires an abstraction layer that translates your intent into each platform's native primitives. That translation layer isn't free. It's not just extra megabytes, it's extra CPU cycles on every frame, extra context switches across the bridge, extra allocations that a garbage collector has to sweep up later. The bloat you see in the binary is a visible artifact of a cost you're also paying, invisibly, in every frame render.

**The dependency tax.** This is the one that compounds silently. npm install a router. It pulls in seven transitive dependencies. Install a state management library. It pulls in its own set, half of which duplicate functionality already sitting in the first package. Nobody audits this because nobody can; the graph is too deep, and the tooling that reports bundle size after the fact only tells you the bill after you've already run up the tab.

None of this is because framework engineers are bad at their jobs. React Native and Flutter are staffed by genuinely excellent people solving a genuinely hard problem: one codebase targeting fundamentally different platforms. But the solution to that problem was never going to be free, and the price gets paid by every single user, on every single install, on every single cold boot, forever, regardless of whether your app needed cross-platform parity in the first place.

## The 500KB Counter-Example

Here's the part where the argument would be empty rhetoric if there wasn't a receipt. So build the same "Hello, World" the other way: Kotlin, native Android views, no cross-platform runtime, no bridge, no bundled JS engine.

```kotlin
class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val tv = TextView(this).apply { text = "Hello, World" }
        setContentView(tv)
    }
}
```

Compile it, minify with R8, strip unused resources. The release APK lands somewhere under 500KB. Not because you tried hard to optimize, but because there was simply nothing extra to cut. The APK contains your compiled bytecode, the Android manifest, and essentially nothing else, because the platform itself already provides the rendering engine, the UI toolkit, and the runtime. You are not fighting a framework's defaults. There are no defaults to fight.

The boot time difference isn't cosmetic either. A native Kotlin Hello World is drawing its first frame before a React Native app has finished initializing its JS runtime, let alone evaluating your first line of application code. On a mid-range Android device (still the majority of the global Android install base, not the flagship phone in your pocket), that difference is the gap between an app that feels instant and one that feels like it's loading a website.

## The Reframe

This is where most "just use native" arguments turn into hipster gatekeeping, and that's not the point being made here. The point isn't that cross-platform frameworks are bad engineering. The point is that binary size and boot latency are not implementation details to be waved off with "storage is cheap" and "phones are fast now." They are user-facing costs, paid on every install and every cold start, and they scale with your user base in a way that your engineering team's convenience does not.

Every megabyte in that APK is a megabyte someone on a data-capped plan in a market where 4G still drops to 3G had to download before they could see your "Hello, World." Every millisecond your JS engine spends initializing is a millisecond your user spent looking at a splash screen instead of your product. These aren't abstractions. They're friction, and friction is the single best predictor of whether someone deletes your app in the first session.

Framework-less development, then, isn't a purity test or a nostalgia trip back to 2012-era native Android. It's a recognition that the platform you're targeting already solved the "how do I draw a UI and run code" problem, and that solving it a second time, inside a bridge, inside a runtime, inside a binary you now have to ship to every user, is a cost that needs to justify itself rather than get assumed by default.

Sometimes it does justify itself. A team shipping the same product to iOS, Android, and web simultaneously, with a small engineering headcount and a tight deadline, has a real argument for paying the abstraction tax; the alternative is tripling the team. That's a legitimate trade.

But "everyone uses React Native" is not that argument. "It's what I already know" is not that argument. And "storage is cheap" stops being true the moment your user is the one paying for the storage, the bandwidth, and the four seconds of their life spent staring at your splash screen, waiting for an interpreter to wake up so it can say hello.

## The Actual Moral Imperative

Ship the framework when the framework earns its weight. Don't ship it because it was the tutorial you followed first. Every dependency you add is a binary someone else has to download, a boot sequence someone else has to sit through, and a battery someone else has to spend keeping your garbage collector fed. That's not a performance nitpick. That's the actual cost of the software you're building, and pretending otherwise doesn't make it disappear. It just moves the bill from your build pipeline to your user's pocket.
