import os
import requests
import socket
import pathlib
import pickle
import re

import time
import traceback

intrinsics = ["tan", "log", "AddUint64", "normalize", "all", "sign", 
"firstbitlow", "cos", "asdouble", "and",    "cosh", "exp", "trunc", 
"ceil", "sin", "WaveActiveMax", "dot4add_i8packed", "dot", "frac",
"WaveIsFirstLane", "rcp", "or", "length", "sinh", "any", "select",
"log2", "lerp", "reversebits",    "exp2", "degrees", "floor",
"radians", "countbits", "mad", "GroupMemoryBarrierWithGroupSync",
"round", "WaveReadLaneAt", "tanh", "WaveActiveAnyTrue", "sqrt",
"max", "dot4add_u8packed",    "log10", "firstbithigh",
"saturate", "atan", "step", "pow", "rsqrt", "abs", "WaveGetLaneIndex",
"cross", "acos", "WaveActiveSum", "clip", "min", "WaveActiveAllTrue",
"isinf", "WaveActiveCountBits",    "atan2", "asin", "asint", "reflect",
"smoothstep", "fmod", "asint16", "asuint", "distance",    "asfloat",
"dot2add", "D3DCOLORtoUBYTE4", "asuint16"]

issue_body = '''In Test\Feature\Intrinsics create, if applicable: (reference the HLSL headers for the types supported by the intrinsic)
- [ ] Test for 16 bit int types (< intrinsic >.int16.test)
- [ ] Test for Half type (< intrinsic >.fp16.test)
- [ ] Test for 32 bit types (< intrinsic >.32.test)
- [ ] Test for 64 bit int types (< intrinsic >.int64.test)
- [ ] Test for Double type (< intrinsic >.fp64.test)

A .test file should contain 
- [ ] a source portion; If multiple .test files can use the same source; it can go in its own file and be referenced in the run portion of each .test file instead. 
```
@@ -0,0 +1,54 @@
#--- source.hlsl

StructuredBuffer<float4> In : register(t0);
RWStructuredBuffer<float> Out : register(u1);

[numthreads(1,1,1)]
void main() {
// A single test can test for all scalar/vector length as shown here.
  Out[0] = length(In[0]); // Test float4
  Out[1] = length(In[1].x); // Test float
  Out[2] = length(In[1].yzw); // Test float3
  Out[3] = length(In[1].yz); // Test float2
}
```
- [ ] a  yaml portion; If multiple .test files can use the same YAML, it can go in its own file and be referenced in the run portion of each  .test file instead.
```
//--- pipeline.yaml

---
Shaders:
  - Stage: Compute
    Entry: main
    DispatchSize: [1, 1, 1]
Buffers:
  - Name: In
    Format: Float32
    Stride: 16
    Data: [ 4, 4, 4, 4, 3.14159, 0, 5, 12 ]
  - Name: Out
    Format: Float32
    Stride: 4
    ZeroInitSize: 12
  - Name: ExpectedOut # The result we expect
    Format: Float32
    Stride: 4
    Data: [ 8, 3.14159, 13, 5 ]
Results:  # A test might have more than 1 result.
  - Result: Test1
    Rule: BufferFuzzy # there is also a BufferExact rule
    ULPT: 1
    Actual: Out
    Expected: ExpectedOut
DescriptorSets:
  - Resources:
    - Name: In
      Kind: StructuredBuffer
      DirectXBinding:
        Register: 0
        Space: 0
      VulkanBinding:
        Binding: 0
    - Name: Out
      Kind: RWStructuredBuffer
      DirectXBinding:
        Register: 1
        Space: 0
      VulkanBinding:
        Binding: 1
...
#--- end
```
- [ ] A run portion; which will be unique to each .test file.  
```
# UNSUPPORTED: Clang-Vulkan
# RUN: split-file %s %t
# RUN: %dxc_target -T cs_6_5 -Fo %t.o %t/source.hlsl
# RUN: %offloader %t/pipeline.yaml %t.o 
```
Currently all tests should include `# UNSUPPORTED: Clang-Vulkan`.
Tests for 16 bit floating point should have a `# REQUIRES: Half`.
Tests for 16 bit integer should have a `# REQUIRES: Int16`.
Tests for 64 bit floating point should have a `# REQUIRES: Double`.
Tests for 64 bit integer should have a `# REQUIRES: Int64`.'''

REPO_OWNER=''
REPO_NAME=''
GITHUB_TOKEN='' # put your personal access token here

def create_github_issue(title, body, labels):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": title,
        "body": body,
        "labels": labels
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        if response.status_code == 201:
            print(f"Successfully created issue: {title}")
            return response.json().get('number')
    except socket.gaierror as e:
        print(f"Socket error: {e}")
    except NameResolutionError as e:
        print(f"Name resolution error: {e}")
    except MaxRetryError as e:
        print(f"Max retries exceeded: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    
    print(f"Failed to create issue: {title}")
    print(f"Response: {response.content}")
    return None

def create_all_issues():
    for i in intrinsics:
        issue_num = create_github_issue(f"Add test for {i}", issue_body, [])
        print(f"created issue #{issue_num}")
    time.sleep(5)

if __name__ == "__main__":
    create_all_issues()
