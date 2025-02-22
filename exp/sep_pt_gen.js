// Generate pTree for a seperate web page
// Usage: Copy the code into the web page console and execute

function createObjectTree(depth_limit = 5, node_limit = 50, debug = false, bl = []) {  //bl: optional blacklist

    class TreeNode {
        constructor(_name) {
            this.name = _name
            this.dict = {}
            this.children = []
        }
    }

    function isArraySetMap(v) {
        if (Array.isArray(v))   return true;
        if (Object.getPrototypeOf(v) === Set.prototype)   return true;
        if (Object.getPrototypeOf(v) === Map.prototype)   return true;
        return false;
    }
    
    function analyzeVariable(v) {
        let v_info = {}
        if (v === undefined) {
            v_info = { dict: { 'type': 'undefined' }, 'children': [] }
        }
        else if (v === null) {
            v_info = { dict: { 'type': 'null' }, 'children': [] }
        }
        else if (isArraySetMap(v)) {
            value = 0
            try{
                value = CryptoJS.MD5(JSON.stringify(v)).toString()
            } catch (e) {
                value = v.length
            }
            v_info = { dict: { 'type': 'array', 'value': value }, 'children': [] }
        }
        else if (typeof (v) == 'string') {
            v_info = { dict: { 'type': 'string', 'value': v.slice(0, 24) }, 'children': [] }
        }
        else if (typeof (v) == 'object') {
            let vlist = Object.getOwnPropertyNames(v)
            vlist = vlist.filter(val => !["prototype"].includes(val));  // Remove name "prototype"
            v_info = { dict: { 'type': 'object' }, 'children': vlist }
        }
        else if (typeof (v) == 'function') {
            let vlist = Object.getOwnPropertyNames(v)
            vlist = vlist.filter(val => !["prototype", "length", "name"].includes(val));
            v_info = { dict: { 'type': 'function' }, 'children': vlist }
        }
        else if (typeof (v) == 'number') {
            v_info = { dict: { 'type': 'number', 'value': v.toFixed(2)}, 'children': [] }
        }
        else {
            v_info = { dict: { 'type': typeof (v), 'value': v }, 'children': [] }
        }
        return v_info
    }


    function hasCircle(v_path) {
        // Prevent loop in the object tree
        // Check whether v points to some parent variable
        if (v_path.length < 1) 
            return false

        cur_v = 'window'
        for (let v of v_path) {
            cur_v += `["${v}"]`
        }
        try{
            if (eval(`typeof (${cur_v}) != 'object' && typeof (${cur_v}) != 'function'`)) 
                return false
        }
        catch{
            return false
        }

        ancient_v = 'window'
        if (eval(`${ancient_v} == ${cur_v}`))
            return true
        for (let i = 0; i < v_path.length - 1; i += 1) {
            ancient_v += `["${v_path[i]}"]`
            try {
                if (eval(`typeof (${ancient_v}) == 'object' || typeof (${ancient_v}) == 'function'`))
                    if (eval(`${ancient_v} == ${cur_v}`))
                        return true
            }
            catch {
                continue
            }
        }

        return false
    }

    // Check whether the property name meet the standard
    function Sanitazer(str) {
        if (str.includes('"'))
            return false
        if (str.length > 24)
            return false
        return true
    }
    

    function genPTree(node_limit, depth_limit, blacklist) {
        // BFS
        let circle_num = 0
        let node_num = 1
        var root = new TreeNode('window')
        let q = []      // Property Path Queue
        let qc = []     // Generated Property Tree Queue
        q.push([])
        qc.push(root)

        while (q.length) {
            let v_path = q.shift()
            let cur_node = qc.shift()

            if (hasCircle(v_path)) {
                circle_num += 1
                continue
            }

            let v_str = 'window'
            for (let v of v_path) {
                if (v == '"') {
                    v_str += `['${v}']`
                }
                else {
                    v_str += `["${v}"]`
                }
            }
            
            if (debug)
                console.log(`${v_str}   depth: ${v_path.length}`)
            
            let v_info = {}
            eval(`v_info = analyzeVariable(${v_str});`)
            if (v_path.length > 0 && cur_node.name != v_path[v_path.length - 1]) {
                console.log('ERROR: UNMATACHED NODES.')
            }

            cur_node.dict = v_info.dict

            // Remove global variables in blacklist
            if (v_path.length == 0) {
                v_info['children'] = v_info['children'].filter(val => !blacklist.includes(val));
            }
            
            if (v_path.length < depth_limit) {
                for (let child of v_info['children']) {
                    if (node_num >= node_limit)
                        break
                    if (!Sanitazer(child))
                        continue    
                    let c_node = new TreeNode(child)
                    cur_node.children.push(c_node)
                    q.push([...v_path])              // shallow copy
                    q[q.length - 1].push(child)
                    qc.push(c_node)
                    node_num += 1
                }
            }
            
        }
        return [root, node_num, circle_num]
    }


    let origin_vlist = ["Object","Function","Array","Number","parseFloat","parseInt","Infinity","NaN","undefined","Boolean","String","Symbol","Date","Promise","RegExp","Error","AggregateError","EvalError","RangeError","ReferenceError","SyntaxError","TypeError","URIError","globalThis","JSON","Math","Intl","ArrayBuffer","Atomics","Uint8Array","Int8Array","Uint16Array","Int16Array","Uint32Array","Int32Array","Float32Array","Float64Array","Uint8ClampedArray","BigUint64Array","BigInt64Array","DataView","Map","BigInt","Set","WeakMap","WeakSet","Proxy","Reflect","FinalizationRegistry","WeakRef","decodeURI","decodeURIComponent","encodeURI","encodeURIComponent","escape","unescape","eval","isFinite","isNaN","console","Option","Image","Audio","webkitURL","webkitRTCPeerConnection","webkitMediaStream","WebKitMutationObserver","WebKitCSSMatrix","XSLTProcessor","XPathResult","XPathExpression","XPathEvaluator","XMLSerializer","XMLHttpRequestUpload","XMLHttpRequestEventTarget","XMLHttpRequest","XMLDocument","WritableStreamDefaultWriter","WritableStreamDefaultController","WritableStream","Worker","Window","WheelEvent","WebSocket","WebGLVertexArrayObject","WebGLUniformLocation","WebGLTransformFeedback","WebGLTexture","WebGLSync","WebGLShaderPrecisionFormat","WebGLShader","WebGLSampler","WebGLRenderingContext","WebGLRenderbuffer","WebGLQuery","WebGLProgram","WebGLFramebuffer","WebGLContextEvent","WebGLBuffer","WebGLActiveInfo","WebGL2RenderingContext","WaveShaperNode","VisualViewport","VirtualKeyboardGeometryChangeEvent","ValidityState","VTTCue","UserActivation","URLSearchParams","URLPattern","URL","UIEvent","TrustedTypePolicyFactory","TrustedTypePolicy","TrustedScriptURL","TrustedScript","TrustedHTML","TreeWalker","TransitionEvent","TransformStreamDefaultController","TransformStream","TrackEvent","TouchList","TouchEvent","Touch","TimeRanges","TextTrackList","TextTrackCueList","TextTrackCue","TextTrack","TextMetrics","TextEvent","TextEncoderStream","TextEncoder","TextDecoderStream","TextDecoder","Text","TaskSignal","TaskPriorityChangeEvent","TaskController","TaskAttributionTiming","SyncManager","SubmitEvent","StyleSheetList","StyleSheet","StylePropertyMapReadOnly","StylePropertyMap","StorageEvent","Storage","StereoPannerNode","StaticRange","SourceBufferList","SourceBuffer","ShadowRoot","Selection","SecurityPolicyViolationEvent","ScriptProcessorNode","ScreenOrientation","Screen","Scheduling","Scheduler","SVGViewElement","SVGUseElement","SVGUnitTypes","SVGTransformList","SVGTransform","SVGTitleElement","SVGTextPositioningElement","SVGTextPathElement","SVGTextElement","SVGTextContentElement","SVGTSpanElement","SVGSymbolElement","SVGSwitchElement","SVGStyleElement","SVGStringList","SVGStopElement","SVGSetElement","SVGScriptElement","SVGSVGElement","SVGRectElement","SVGRect","SVGRadialGradientElement","SVGPreserveAspectRatio","SVGPolylineElement","SVGPolygonElement","SVGPointList","SVGPoint","SVGPatternElement","SVGPathElement","SVGNumberList","SVGNumber","SVGMetadataElement","SVGMatrix","SVGMaskElement","SVGMarkerElement","SVGMPathElement","SVGLinearGradientElement","SVGLineElement","SVGLengthList","SVGLength","SVGImageElement","SVGGraphicsElement","SVGGradientElement","SVGGeometryElement","SVGGElement","SVGForeignObjectElement","SVGFilterElement","SVGFETurbulenceElement","SVGFETileElement","SVGFESpotLightElement","SVGFESpecularLightingElement","SVGFEPointLightElement","SVGFEOffsetElement","SVGFEMorphologyElement","SVGFEMergeNodeElement","SVGFEMergeElement","SVGFEImageElement","SVGFEGaussianBlurElement","SVGFEFuncRElement","SVGFEFuncGElement","SVGFEFuncBElement","SVGFEFuncAElement","SVGFEFloodElement","SVGFEDropShadowElement","SVGFEDistantLightElement","SVGFEDisplacementMapElement","SVGFEDiffuseLightingElement","SVGFEConvolveMatrixElement","SVGFECompositeElement","SVGFEComponentTransferElement","SVGFEColorMatrixElement","SVGFEBlendElement","SVGEllipseElement","SVGElement","SVGDescElement","SVGDefsElement","SVGComponentTransferFunctionElement","SVGClipPathElement","SVGCircleElement","SVGAnimationElement","SVGAnimatedTransformList","SVGAnimatedString","SVGAnimatedRect","SVGAnimatedPreserveAspectRatio","SVGAnimatedNumberList","SVGAnimatedNumber","SVGAnimatedLengthList","SVGAnimatedLength","SVGAnimatedInteger","SVGAnimatedEnumeration","SVGAnimatedBoolean","SVGAnimatedAngle","SVGAnimateTransformElement","SVGAnimateMotionElement","SVGAnimateElement","SVGAngle","SVGAElement","Response","ResizeObserverSize","ResizeObserverEntry","ResizeObserver","Request","ReportingObserver","ReadableStreamDefaultReader","ReadableStreamDefaultController","ReadableStreamBYOBRequest","ReadableStreamBYOBReader","ReadableStream","ReadableByteStreamController","Range","RadioNodeList","RTCTrackEvent","RTCStatsReport","RTCSessionDescription","RTCSctpTransport","RTCRtpTransceiver","RTCRtpSender","RTCRtpReceiver","RTCPeerConnectionIceEvent","RTCPeerConnectionIceErrorEvent","RTCPeerConnection","RTCIceTransport","RTCIceCandidate","RTCErrorEvent","RTCError","RTCEncodedVideoFrame","RTCEncodedAudioFrame","RTCDtlsTransport","RTCDataChannelEvent","RTCDataChannel","RTCDTMFToneChangeEvent","RTCDTMFSender","RTCCertificate","PromiseRejectionEvent","ProgressEvent","Profiler","ProcessingInstruction","PopStateEvent","PointerEvent","PluginArray","Plugin","PictureInPictureWindow","PictureInPictureEvent","PeriodicWave","PerformanceTiming","PerformanceServerTiming","PerformanceResourceTiming","PerformancePaintTiming","PerformanceObserverEntryList","PerformanceObserver","PerformanceNavigationTiming","PerformanceNavigation","PerformanceMeasure","PerformanceMark","PerformanceLongTaskTiming","PerformanceEventTiming","PerformanceEntry","PerformanceElementTiming","Performance","Path2D","PannerNode","PageTransitionEvent","OverconstrainedError","OscillatorNode","OffscreenCanvasRenderingContext2D","OffscreenCanvas","OfflineAudioContext","OfflineAudioCompletionEvent","NodeList","NodeIterator","NodeFilter","Node","NetworkInformation","Navigator","NavigationTransition","NavigationHistoryEntry","NavigationDestination","NavigationCurrentEntryChangeEvent","Navigation","NavigateEvent","NamedNodeMap","MutationRecord","MutationObserver","MouseEvent","MimeTypeArray","MimeType","MessagePort","MessageEvent","MessageChannel","MediaStreamTrackProcessor","MediaStreamTrackGenerator","MediaStreamTrackEvent","MediaStreamTrack","MediaStreamEvent","MediaStreamAudioSourceNode","MediaStreamAudioDestinationNode","MediaStream","MediaSourceHandle","MediaSource","MediaRecorder","MediaQueryListEvent","MediaQueryList","MediaList","MediaError","MediaEncryptedEvent","MediaElementAudioSourceNode","MediaCapabilities","MathMLElement","Location","LayoutShiftAttribution","LayoutShift","LargestContentfulPaint","KeyframeEffect","KeyboardEvent","IntersectionObserverEntry","IntersectionObserver","InputEvent","InputDeviceInfo","InputDeviceCapabilities","ImageData","ImageCapture","ImageBitmapRenderingContext","ImageBitmap","IdleDeadline","IIRFilterNode","IDBVersionChangeEvent","IDBTransaction","IDBRequest","IDBOpenDBRequest","IDBObjectStore","IDBKeyRange","IDBIndex","IDBFactory","IDBDatabase","IDBCursorWithValue","IDBCursor","History","Headers","HashChangeEvent","HTMLVideoElement","HTMLUnknownElement","HTMLUListElement","HTMLTrackElement","HTMLTitleElement","HTMLTimeElement","HTMLTextAreaElement","HTMLTemplateElement","HTMLTableSectionElement","HTMLTableRowElement","HTMLTableElement","HTMLTableColElement","HTMLTableCellElement","HTMLTableCaptionElement","HTMLStyleElement","HTMLSpanElement","HTMLSourceElement","HTMLSlotElement","HTMLSelectElement","HTMLScriptElement","HTMLQuoteElement","HTMLProgressElement","HTMLPreElement","HTMLPictureElement","HTMLParamElement","HTMLParagraphElement","HTMLOutputElement","HTMLOptionsCollection","HTMLOptionElement","HTMLOptGroupElement","HTMLObjectElement","HTMLOListElement","HTMLModElement","HTMLMeterElement","HTMLMetaElement","HTMLMenuElement","HTMLMediaElement","HTMLMarqueeElement","HTMLMapElement","HTMLLinkElement","HTMLLegendElement","HTMLLabelElement","HTMLLIElement","HTMLInputElement","HTMLImageElement","HTMLIFrameElement","HTMLHtmlElement","HTMLHeadingElement","HTMLHeadElement","HTMLHRElement","HTMLFrameSetElement","HTMLFrameElement","HTMLFormElement","HTMLFormControlsCollection","HTMLFontElement","HTMLFieldSetElement","HTMLEmbedElement","HTMLElement","HTMLDocument","HTMLDivElement","HTMLDirectoryElement","HTMLDialogElement","HTMLDetailsElement","HTMLDataListElement","HTMLDataElement","HTMLDListElement","HTMLCollection","HTMLCanvasElement","HTMLButtonElement","HTMLBodyElement","HTMLBaseElement","HTMLBRElement","HTMLAudioElement","HTMLAreaElement","HTMLAnchorElement","HTMLAllCollection","GeolocationPositionError","GeolocationPosition","GeolocationCoordinates","Geolocation","GamepadHapticActuator","GamepadEvent","GamepadButton","Gamepad","GainNode","FormDataEvent","FormData","FontFaceSetLoadEvent","FontFace","FocusEvent","FileReader","FileList","File","FeaturePolicy","External","EventTarget","EventSource","EventCounts","Event","ErrorEvent","ElementInternals","Element","DynamicsCompressorNode","DragEvent","DocumentType","DocumentFragment","Document","DelayNode","DecompressionStream","DataTransferItemList","DataTransferItem","DataTransfer","DOMTokenList","DOMStringMap","DOMStringList","DOMRectReadOnly","DOMRectList","DOMRect","DOMQuad","DOMPointReadOnly","DOMPoint","DOMParser","DOMMatrixReadOnly","DOMMatrix","DOMImplementation","DOMException","DOMError","CustomStateSet","CustomEvent","CustomElementRegistry","Crypto","CountQueuingStrategy","ConvolverNode","ConstantSourceNode","CompressionStream","CompositionEvent","Comment","CloseEvent","ClipboardEvent","CharacterData","ChannelSplitterNode","ChannelMergerNode","CanvasRenderingContext2D","CanvasPattern","CanvasGradient","CanvasCaptureMediaStreamTrack","CSSVariableReferenceValue","CSSUnparsedValue","CSSUnitValue","CSSTranslate","CSSTransformValue","CSSTransformComponent","CSSSupportsRule","CSSStyleValue","CSSStyleSheet","CSSStyleRule","CSSStyleDeclaration","CSSSkewY","CSSSkewX","CSSSkew","CSSScale","CSSRuleList","CSSRule","CSSRotate","CSSPropertyRule","CSSPositionValue","CSSPerspective","CSSPageRule","CSSNumericValue","CSSNumericArray","CSSNamespaceRule","CSSMediaRule","CSSMatrixComponent","CSSMathValue","CSSMathSum","CSSMathProduct","CSSMathNegate","CSSMathMin","CSSMathMax","CSSMathInvert","CSSMathClamp","CSSLayerStatementRule","CSSLayerBlockRule","CSSKeywordValue","CSSKeyframesRule","CSSKeyframeRule","CSSImportRule","CSSImageValue","CSSGroupingRule","CSSFontPaletteValuesRule","CSSFontFaceRule","CSSCounterStyleRule","CSSContainerRule","CSSConditionRule","CSS","CDATASection","ByteLengthQueuingStrategy","BroadcastChannel","BlobEvent","Blob","BiquadFilterNode","BeforeUnloadEvent","BeforeInstallPromptEvent","BaseAudioContext","BarProp","AudioWorkletNode","AudioSinkInfo","AudioScheduledSourceNode","AudioProcessingEvent","AudioParamMap","AudioParam","AudioNode","AudioListener","AudioDestinationNode","AudioContext","AudioBufferSourceNode","AudioBuffer","Attr","AnimationEvent","AnimationEffect","Animation","AnalyserNode","AbstractRange","AbortSignal","AbortController","window","self","document","name","location","customElements","history","navigation","locationbar","menubar","personalbar","scrollbars","statusbar","toolbar","status","closed","frames","length","top","opener","parent","frameElement","navigator","origin","external","screen","innerWidth","innerHeight","scrollX","pageXOffset","scrollY","pageYOffset","visualViewport","screenX","screenY","outerWidth","outerHeight","devicePixelRatio","event","clientInformation","offscreenBuffering","screenLeft","screenTop","styleMedia","onsearch","isSecureContext","trustedTypes","performance","onappinstalled","onbeforeinstallprompt","crypto","indexedDB","sessionStorage","localStorage","onbeforexrselect","onabort","onbeforeinput","onblur","oncancel","oncanplay","oncanplaythrough","onchange","onclick","onclose","oncontextlost","oncontextmenu","oncontextrestored","oncuechange","ondblclick","ondrag","ondragend","ondragenter","ondragleave","ondragover","ondragstart","ondrop","ondurationchange","onemptied","onended","onerror","onfocus","onformdata","oninput","oninvalid","onkeydown","onkeypress","onkeyup","onload","onloadeddata","onloadedmetadata","onloadstart","onmousedown","onmouseenter","onmouseleave","onmousemove","onmouseout","onmouseover","onmouseup","onmousewheel","onpause","onplay","onplaying","onprogress","onratechange","onreset","onresize","onscroll","onsecuritypolicyviolation","onseeked","onseeking","onselect","onslotchange","onstalled","onsubmit","onsuspend","ontimeupdate","ontoggle","onvolumechange","onwaiting","onwebkitanimationend","onwebkitanimationiteration","onwebkitanimationstart","onwebkittransitionend","onwheel","onauxclick","ongotpointercapture","onlostpointercapture","onpointerdown","onpointermove","onpointerrawupdate","onpointerup","onpointercancel","onpointerover","onpointerout","onpointerenter","onpointerleave","onselectstart","onselectionchange","onanimationend","onanimationiteration","onanimationstart","ontransitionrun","ontransitionstart","ontransitionend","ontransitioncancel","onafterprint","onbeforeprint","onbeforeunload","onhashchange","onlanguagechange","onmessage","onmessageerror","onoffline","ononline","onpagehide","onpageshow","onpopstate","onrejectionhandled","onstorage","onunhandledrejection","onunload","crossOriginIsolated","scheduler","alert","atob","blur","btoa","cancelAnimationFrame","cancelIdleCallback","captureEvents","clearInterval","clearTimeout","close","confirm","createImageBitmap","fetch","find","focus","getComputedStyle","getSelection","matchMedia","moveBy","moveTo","open","postMessage","print","prompt","queueMicrotask","releaseEvents","reportError","requestAnimationFrame","requestIdleCallback","resizeBy","resizeTo","scroll","scrollBy","scrollTo","setInterval","setTimeout","stop","structuredClone","webkitCancelAnimationFrame","webkitRequestAnimationFrame","chrome","WebAssembly","fence","caches","cookieStore","ondevicemotion","ondeviceorientation","ondeviceorientationabsolute","launchQueue","sharedStorage","documentPictureInPicture","onbeforematch","onbeforetoggle","AbsoluteOrientationSensor","Accelerometer","AudioWorklet","BatteryManager","Cache","CacheStorage","Clipboard","ClipboardItem","CookieChangeEvent","CookieStore","CookieStoreManager","Credential","CredentialsContainer","CryptoKey","DeviceMotionEvent","DeviceMotionEventAcceleration","DeviceMotionEventRotationRate","DeviceOrientationEvent","FederatedCredential","GPU","GPUAdapter","GPUAdapterInfo","GPUBindGroup","GPUBindGroupLayout","GPUBuffer","GPUBufferUsage","GPUCanvasContext","GPUColorWrite","GPUCommandBuffer","GPUCommandEncoder","GPUCompilationInfo","GPUCompilationMessage","GPUComputePassEncoder","GPUComputePipeline","GPUDevice","GPUDeviceLostInfo","GPUError","GPUExternalTexture","GPUInternalError","GPUMapMode","GPUOutOfMemoryError","GPUPipelineError","GPUPipelineLayout","GPUQuerySet","GPUQueue","GPURenderBundle","GPURenderBundleEncoder","GPURenderPassEncoder","GPURenderPipeline","GPUSampler","GPUShaderModule","GPUShaderStage","GPUSupportedFeatures","GPUSupportedLimits","GPUTexture","GPUTextureUsage","GPUTextureView","GPUUncapturedErrorEvent","GPUValidationError","GravitySensor","Gyroscope","Keyboard","KeyboardLayoutMap","LinearAccelerationSensor","Lock","LockManager","MIDIAccess","MIDIConnectionEvent","MIDIInput","MIDIInputMap","MIDIMessageEvent","MIDIOutput","MIDIOutputMap","MIDIPort","MediaDeviceInfo","MediaDevices","MediaKeyMessageEvent","MediaKeySession","MediaKeyStatusMap","MediaKeySystemAccess","MediaKeys","NavigationPreloadManager","NavigatorManagedData","OrientationSensor","PasswordCredential","RelativeOrientationSensor","Sanitizer","ScreenDetailed","ScreenDetails","Sensor","SensorErrorEvent","ServiceWorker","ServiceWorkerContainer","ServiceWorkerRegistration","StorageManager","SubtleCrypto","VirtualKeyboard","WGSLLanguageFeatures","WebTransport","WebTransportBidirectionalStream","WebTransportDatagramDuplexStream","WebTransportError","Worklet","XRDOMOverlayState","XRLayer","XRWebGLBinding","AudioData","EncodedAudioChunk","EncodedVideoChunk","ImageTrack","ImageTrackList","VideoColorSpace","VideoFrame","AudioDecoder","AudioEncoder","ImageDecoder","VideoDecoder","VideoEncoder","AuthenticatorAssertionResponse","AuthenticatorAttestationResponse","AuthenticatorResponse","PublicKeyCredential","BarcodeDetector","Bluetooth","BluetoothCharacteristicProperties","BluetoothDevice","BluetoothRemoteGATTCharacteristic","BluetoothRemoteGATTDescriptor","BluetoothRemoteGATTServer","BluetoothRemoteGATTService","CaptureController","DocumentPictureInPicture","EyeDropper","Fence","FencedFrameConfig","HTMLFencedFrameElement","FileSystemDirectoryHandle","FileSystemFileHandle","FileSystemHandle","FileSystemWritableFileStream","FontData","FragmentDirective","HID","HIDConnectionEvent","HIDDevice","HIDInputReportEvent","IdentityCredential","IdentityProvider","IdleDetector","LaunchParams","LaunchQueue","OTPCredential","PaymentAddress","PaymentRequest","PaymentResponse","PaymentMethodChangeEvent","Presentation","PresentationAvailability","PresentationConnection","PresentationConnectionAvailableEvent","PresentationConnectionCloseEvent","PresentationConnectionList","PresentationReceiver","PresentationRequest","Serial","SerialPort","SharedStorage","SharedStorageWorklet","ToggleEvent","USB","USBAlternateInterface","USBConfiguration","USBConnectionEvent","USBDevice","USBEndpoint","USBInTransferResult","USBInterface","USBIsochronousInTransferPacket","USBIsochronousInTransferResult","USBIsochronousOutTransferPacket","USBIsochronousOutTransferResult","USBOutTransferResult","WakeLock","WakeLockSentinel","WindowControlsOverlay","WindowControlsOverlayGeometryChangeEvent","XRAnchor","XRAnchorSet","XRBoundedReferenceSpace","XRCPUDepthInformation","XRCamera","XRDepthInformation","XRFrame","XRHitTestResult","XRHitTestSource","XRInputSource","XRInputSourceArray","XRInputSourceEvent","XRInputSourcesChangeEvent","XRLightEstimate","XRLightProbe","XRPose","XRRay","XRReferenceSpace","XRReferenceSpaceEvent","XRRenderState","XRRigidTransform","XRSession","XRSessionEvent","XRSpace","XRSystem","XRTransientInputHitTestResult","XRTransientInputHitTestSource","XRView","XRViewerPose","XRViewport","XRWebGLDepthInformation","XRWebGLLayer","getScreenDetails","openDatabase","queryLocalFonts","showDirectoryPicker","showOpenFilePicker","showSaveFilePicker","originAgentCluster","credentialless","speechSynthesis","oncontentvisibilityautostatechange","onscrollend","AnimationPlaybackEvent","AnimationTimeline","CSSAnimation","CSSTransition","DocumentTimeline","BackgroundFetchManager","BackgroundFetchRecord","BackgroundFetchRegistration","BluetoothUUID","BrowserCaptureMediaStreamTrack","CropTarget","CSSStartingStyleRule","ContentVisibilityAutoStateChangeEvent","DelegatedInkTrailPresenter","Ink","DocumentPictureInPictureEvent","Highlight","HighlightRegistry","MediaMetadata","MediaSession","MutationEvent","NavigatorUAData","Notification","PaymentManager","PaymentRequestUpdateEvent","PeriodicSyncManager","PermissionStatus","Permissions","PushManager","PushSubscription","PushSubscriptionOptions","RemotePlayback","ScrollTimeline","ViewTimeline","SharedWorker","SpeechSynthesisErrorEvent","SpeechSynthesisEvent","SpeechSynthesisUtterance","VideoPlaybackQuality","ViewTransition","VisibilityStateEntry","webkitSpeechGrammar","webkitSpeechGrammarList","webkitSpeechRecognition","webkitSpeechRecognitionError","webkitSpeechRecognitionEvent","webkitRequestFileSystem","webkitResolveLocalFileSystemURL","createObjectTree","getGlobalV","__REACT_DEVTOOLS_APPEND_COMPONENT_STACK__","__REACT_DEVTOOLS_BREAK_ON_CONSOLE_ERRORS__","__REACT_DEVTOOLS_COMPONENT_FILTERS__","__REACT_DEVTOOLS_SHOW_INLINE_WARNINGS_AND_ERRORS__","__REACT_DEVTOOLS_HIDE_CONSOLE_LOGS_IN_STRICT_MODE__","__REACT_DEVTOOLS_BROWSER_THEME__","cur_v","ancient_v","dir","dirxml","profile","profileEnd","clear","table","keys","values","debug","undebug","monitor","unmonitor","inspect","copy","queryObjects","$_","$0","$1","$2","$3","$4","getEventListeners","getAccessibleName","getAccessibleRole","monitorEvents","unmonitorEvents","$$","$x","CryptoJS","CSSScopeRule"];
    let tree_info = genPTree(node_limit, depth_limit, [...origin_vlist, ...bl])
    let tree = tree_info[0]

    if (debug) {
        console.log(`Node number: ${tree_info[1]}   Circle number: ${tree_info[2]}`)
        console.log(tree)
    }

    console.log('Following is the JSON format tree. May copy it for other usage.')
    console.log(JSON.stringify(tree));
}

createObjectTree(5, 500, true);