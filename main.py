import streamlit as st
import streamlit.components.v1 as components
import random
import time

# 1. 페이지 및 화면 전체 채우기 설정 (CSS)
st.set_page_config(page_title="공룡 시대 생존기", page_icon="🦖", layout="wide")

st.markdown("""
    <style>
    /* Streamlit 기본 여백 제거 및 전체 화면 구성 */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .subtitle-box {
        background-color: rgba(0, 0, 0, 0.85);
        color: #00ff66;
        padding: 15px 20px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 18px;
        text-align: center;
        border: 2px solid #00ff66;
        margin-top: 10px;
    }
    .egg-crack {
        text-align: center;
        font-size: 80px;
        user-select: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- 데이터 정의 ---
ERA_DATA = {
    "트라이아스기": {
        "desc": "초대륙 판게아의 건조하고 뜨거운 땅. 초기 공룡들이 막 등장하기 시작한 시대입니다.",
        "dinos": [
            {"name": "에오랍토르", "color": "#00ff88", "hp": 80, "desc": "크기는 작지만 날렵한 잡식 공룡"},
            {"name": "코엘로피시스", "color": "#ffaa00", "hp": 70, "desc": "날카로운 이빨을 가진 빠른 육식 공룡"}
        ],
        "events": [
            "가뭄이 시작되었습니다. 물을 찾아 이동합니다.",
            "작은 소형 파충류 무리를 발견하여 배를 채웠습니다.",
            "갑작스러운 모래폭풍이 몰아칩니다!"
        ]
    },
    "쥐라기": {
        "desc": "울창한 침엽수림과 거대한 용각류가 지배하는 온난한 시대입니다.",
        "dinos": [
            {"name": "알로사우루스", "color": "#ff3333", "hp": 120, "desc": "쥐라기 최고의 맹렬한 포식자"},
            {"name": "스테고사우루스", "color": "#3388ff", "hp": 150, "desc": "등의 골판과 꼬리 가시를 가진 초식 공룡"}
        ],
        "events": [
            "거대한 브라키오사우루스 무리가 지나가며 열매를 떨어뜨렸습니다.",
            "숲 속에서 다른 육식 공룡과 영역 다툼이 벌어졌습니다.",
            "신선한 침엽수 잎과 물웅덩이를 찾았습니다."
        ]
    },
    "백악기": {
        "desc": "공룡의 황금기. 최강의 공룡들이 다양하게 진화한 시대입니다.",
        "dinos": [
            {"name": "티라노사우루스", "color": "#cc0000", "hp": 150, "desc": "압도적인 턱 힘을 가진 백악기의 제왕"},
            {"name": "트리케라톱스", "color": "#885522", "hp": 180, "desc": "세 개의 뿔과 단단한 프릴을 가진 초식 공룡"}
        ],
        "events": [
            "화산 재가 내리기 시작합니다. 안전한 곳으로 이동해야 합니다.",
            "사냥에 성공하여 든든하게 배를 채웠습니다.",
            "새로운 종류의 속씨식물 열매를 발견했습니다."
        ]
    }
}

# --- 세션 상태 초기화 ---
if 'stage' not in st.session_state:
    st.session_state.stage = 'TITLE'  # TITLE -> STORY_3D -> ERA_SELECT -> FLASH -> EGG -> DINO_3D -> PLAYING
if 'selected_era' not in st.session_state:
    st.session_state.selected_era = None
if 'player_dino' not in st.session_state:
    st.session_state.player_dino = None
if 'crack_count' not in st.session_state:
    st.session_state.crack_count = 0
if 'hp' not in st.session_state:
    st.session_state.hp = 100
if 'day' not in st.session_state:
    st.session_state.day = 1
if 'logs' not in st.session_state:
    st.session_state.logs = []

# --- 3D 1인칭 직접 조작 캔버스 (마우스 드래그 및 키보드 통합 컨트롤) ---
def render_interactive_3d_world():
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; overflow: hidden; font-family: sans-serif; background: #000; }
            #canvas-container { width: 100vw; height: 70vh; position: relative; user-select: none; }
            #ui-box {
                position: absolute; bottom: 15px; left: 50%;
                transform: translateX(-50%);
                background: rgba(0,0,0,0.85); color: #00ff66;
                padding: 10px 20px; border-radius: 8px;
                border: 2px solid #00ff66; font-size: 16px; text-align: center;
                z-index: 5; pointer-events: none;
            }
            #door-btn {
                position: absolute; top: 15px; left: 50%;
                transform: translateX(-50%);
                background: #ffcc00; color: #000; font-weight: bold;
                padding: 12px 24px; border-radius: 8px; font-size: 18px;
                border: none; cursor: pointer; display: none; z-index: 20;
                box-shadow: 0 0 10px #ffcc00;
            }
            #guide-overlay {
                position: absolute; top: 10px; left: 10px;
                background: rgba(0,0,0,0.6); color: #fff;
                padding: 8px 12px; border-radius: 6px; font-size: 13px;
                z-index: 10; pointer-events: none;
            }
        </style>
    </head>
    <body>
        <div id="canvas-container">
            <div id="guide-overlay">
                🕹️ <b>조작방법:</b><br>
                - 이동: <b>W, A, S, D</b> 키<br>
                - 시점 회전: <b>마우스 클릭 후 드래그</b>
            </div>
            <button id="door-btn" onclick="doorInteract()">🚪 집 밖으로 나가기</button>
            <div id="ui-box">💬 거실을 탐색하세요! 현관문(오른쪽 벽) 근처로 이동하면 나갈 수 있습니다.</div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

        <script>
            let container = document.getElementById('canvas-container');
            let scene = new THREE.Scene();
            let camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            let renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);

            let uiBox = document.getElementById('ui-box');
            let doorBtn = document.getElementById('door-btn');

            let currentZone = 0; // 0: 집 안, 1: 도시

            // 이동 및 마우스 드래그 변수
            let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
            let isMouseDown = false;
            let mouseX = 0, mouseY = 0;
            let lon = -90, lat = 0;
            let phi = 0, theta = 0;

            // 이벤트 리스너: 키보드 이동
            window.addEventListener('keydown', (e) => {
                switch (e.code) {
                    case 'KeyW': moveForward = true; break;
                    case 'KeyA': moveLeft = true; break;
                    case 'KeyS': moveBackward = true; break;
                    case 'KeyD': moveRight = true; break;
                }
            });
            window.addEventListener('keyup', (e) => {
                switch (e.code) {
                    case 'KeyW': moveForward = false; break;
                    case 'KeyA': moveLeft = false; break;
                    case 'KeyS': moveBackward = false; break;
                    case 'KeyD': moveRight = false; break;
                }
            });

            // 이벤트 리스너: 마우스 드래그 시점 회전
            container.addEventListener('mousedown', (e) => {
                isMouseDown = true;
                mouseX = e.clientX;
                mouseY = e.clientY;
            });
            window.addEventListener('mouseup', () => { isMouseDown = false; });
            window.addEventListener('mousemove', (e) => {
                if (isMouseDown) {
                    lon += (e.clientX - mouseX) * 0.25;
                    lat -= (e.clientY - mouseY) * 0.25;
                    lat = Math.max(-85, Math.min(85, lat));
                    mouseX = e.clientX;
                    mouseY = e.clientY;
                }
            });

            // --- 월드 구축 ---
            let houseGroup = new THREE.Group();
            let cityGroup = new THREE.Group();
            let ufoGroup = new THREE.Group();

            function buildHouse() {
                scene.background = new THREE.Color(0x1a1a1a);
                // 바닥
                let floor = new THREE.Mesh(new THREE.PlaneGeometry(20, 20), new THREE.MeshStandardMaterial({ color: 0x8b5a2b }));
                floor.rotation.x = -Math.PI / 2;
                houseGroup.add(floor);
                // 벽
                let wallMat = new THREE.MeshStandardMaterial({ color: 0xdddddd });
                let wall1 = new THREE.Mesh(new THREE.BoxGeometry(20, 5, 0.2), wallMat); wall1.position.set(0, 2.5, -10);
                let wall2 = new THREE.Mesh(new THREE.BoxGeometry(20, 5, 0.2), wallMat); wall2.position.set(0, 2.5, 10);
                let wall3 = new THREE.Mesh(new THREE.BoxGeometry(0.2, 5, 20), wallMat); wall3.position.set(-10, 2.5, 0);
                houseGroup.add(wall1, wall2, wall3);

                // 현관문
                let doorMat = new THREE.MeshStandardMaterial({ color: 0x553311 });
                let door = new THREE.Mesh(new THREE.BoxGeometry(0.2, 4, 2), doorMat);
                door.position.set(9.9, 2, 0);
                houseGroup.add(door);

                // 가구
                let sofa = new THREE.Mesh(new THREE.BoxGeometry(3, 1, 1.5), new THREE.MeshStandardMaterial({ color: 0x992222 }));
                sofa.position.set(-5, 0.5, -5);
                houseGroup.add(sofa);

                scene.add(houseGroup);
                camera.position.set(0, 1.6, 0);
            }

            function buildCity() {
                scene.remove(houseGroup);
                scene.background = new THREE.Color(0x87ceeb);

                let road = new THREE.Mesh(new THREE.PlaneGeometry(50, 100), new THREE.MeshStandardMaterial({ color: 0x444444 }));
                road.rotation.x = -Math.PI / 2;
                cityGroup.add(road);

                for(let i = -40; i <= 40; i += 20) {
                    let b1 = new THREE.Mesh(new THREE.BoxGeometry(10, 15 + Math.random()*10, 10), new THREE.MeshStandardMaterial({ color: 0x778899 }));
                    b1.position.set(-15, 8, i);
                    let b2 = new THREE.Mesh(new THREE.BoxGeometry(10, 15 + Math.random()*10, 10), new THREE.MeshStandardMaterial({ color: 0x778899 }));
                    b2.position.set(15, 8, i);
                    cityGroup.add(b1, b2);
                }

                // 아이스크림 가게
                let shop = new THREE.Mesh(new THREE.BoxGeometry(8, 6, 8), new THREE.MeshStandardMaterial({ color: 0xff6699 }));
                shop.position.set(0, 3, -35);
                cityGroup.add(shop);

                // UFO
                let ufoDisc = new THREE.Mesh(new THREE.CylinderGeometry(5, 5, 1, 16), new THREE.MeshStandardMaterial({ color: 0x888888 }));
                let ufoDome = new THREE.Mesh(new THREE.SphereGeometry(2.5, 16, 16), new THREE.MeshStandardMaterial({ color: 0x00ff00, transparent: true, opacity: 0.7 }));
                ufoDome.position.y = 0.5;
                ufoGroup.add(ufoDisc, ufoDome);
                ufoGroup.position.set(0, 20, -20);
                cityGroup.add(ufoGroup);

                scene.add(cityGroup);
                camera.position.set(0, 1.6, 30);
                uiBox.innerText = "🍦 저기 멀리 보이는 분홍색 아이스크림 가게로 전진(W)하세요!";
            }

            // 조명
            let light = new THREE.DirectionalLight(0xffffff, 1);
            light.position.set(10, 20, 10);
            scene.add(light);
            scene.add(new THREE.AmbientLight(0xffffff, 0.6));

            buildHouse();

            window.doorInteract = function() {
                currentZone = 1;
                doorBtn.style.display = 'none';
                buildCity();
            };

            let captured = false;
            let speed = 0.15;

            function animate() {
                requestAnimationFrame(animate);

                // 시점 계산
                lat = Math.max(-85, Math.min(85, lat));
                phi = THREE.MathUtils.degToRad(90 - lat);
                theta = THREE.MathUtils.degToRad(lon);

                let target = new THREE.Vector3();
                target.x = camera.position.x + 100 * Math.sin(phi) * Math.cos(theta);
                target.y = camera.position.y + 100 * Math.cos(phi);
                target.z = camera.position.z + 100 * Math.sin(phi) * Math.sin(theta);
                camera.lookAt(target);

                // 이동 계산
                let dir = new THREE.Vector3();
                camera.getWorldDirection(dir);
                dir.y = 0;
                dir.normalize();

                let sideDir = new THREE.Vector3(-dir.z, 0, dir.x);

                if (moveForward) camera.position.addScaledVector(dir, speed);
                if (moveBackward) camera.position.addScaledVector(dir, -speed);
                if (moveLeft) camera.position.addScaledVector(sideDir, -speed);
                if (moveRight) camera.position.addScaledVector(sideDir, speed);

                // 현관문 체크
                if (currentZone === 0) {
                    if (camera.position.x > 7.0 && Math.abs(camera.position.z) < 3.0) {
                        doorBtn.style.display = 'block';
                        uiBox.innerText = "🚪 현관문 앞입니다! 버튼을 눌러 밖으로 나가세요.";
                    } else {
                        doorBtn.style.display = 'none';
                        uiBox.innerText = "💬 W,A,S,D키로 이동하여 현관문(오른쪽 벽)으로 가세요.";
                    }
                }

                // UFO 납치 체크
                if (currentZone === 1 && !captured) {
                    if (camera.position.z < 0) {
                        captured = true;
                        uiBox.innerText = "🛸 하늘에서 초록 외계인 UFO가 나타나 당신을 빨아들입니다!!";
                        
                        let beam = new THREE.Mesh(new THREE.CylinderGeometry(2, 5, 25, 16), new THREE.MeshBasicMaterial({ color: 0x00ff00, transparent: true, opacity: 0.6 }));
                        beam.position.set(0, 10, camera.position.z);
                        scene.add(beam);
                    }
                }

                renderer.render(scene, camera);
            }

            animate();
        </script>
    </body>
    </html>
    """
    # pointer-lock 브라우저 제한 우회를 위해 마우스 드래그 방식 사용
    components.html(html_code, height=620)

# 3D 공룡 렌더링
def render_3d_dino(dino_name, dino_color):
    html_code = f"""
    <div id="dino-3d-container" style="width: 100%; height: 350px; background-color: #111; border-radius: 10px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const container = document.getElementById('dino-3d-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(5, 10, 7);
        scene.add(dirLight);

        const dinoGroup = new THREE.Group();
        const material = new THREE.MeshStandardMaterial({{ color: '{dino_color}', roughness: 0.4 }});

        const body = new THREE.Mesh(new THREE.BoxGeometry(1.5, 1.2, 2), material);
        dinoGroup.add(body);
        const head = new THREE.Mesh(new THREE.BoxGeometry(1, 0.9, 1.3), material);
        head.position.set(0, 0.8, 1.2);
        dinoGroup.add(head);
        const tail = new THREE.Mesh(new THREE.ConeGeometry(0.5, 2.5, 8), material);
        tail.rotation.x = -Math.PI / 3;
        tail.position.set(0, -0.2, -1.8);
        dinoGroup.add(tail);

        const legGeo = new THREE.CylinderGeometry(0.3, 0.3, 1.2, 8);
        const leg1 = new THREE.Mesh(legGeo, material); leg1.position.set(-0.6, -1, 0);
        const leg2 = new THREE.Mesh(legGeo, material); leg2.position.set(0.6, -1, 0);
        dinoGroup.add(leg1); dinoGroup.add(leg2);

        scene.add(dinoGroup);
        camera.position.set(3, 2, 5);
        camera.lookAt(0, 0, 0);

        function animate() {{
            requestAnimationFrame(animate);
            dinoGroup.rotation.y += 0.02;
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(html_code, height=370)

# ==========================================
# 게임 단계 제어
# ==========================================

# 0. 메인 시작 화면
if st.session_state.stage == 'TITLE':
    st.markdown("<h1 style='text-align: center; margin-top: 80px;'>🦖 공룡 시대 생존기 🛸</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>일상에서 공룡 시대로! 1인칭 직접 조작 생존 게임</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎮 게임 시작하기", use_container_width=True):
            st.session_state.stage = 'STORY_3D'
            st.rerun()

# 1. 3D 직접 조작 탐색
elif st.session_state.stage == 'STORY_3D':
    st.write("🎮 **조작 가이드:** 화면을 클릭한 채로 드래그하면 **360도 시점 변경**, **W, A, S, D**키로 이동합니다.")
    
    render_interactive_3d_world()
    
    if st.button("🌀 UFO에 납치되어 다음 단계로 진행", use_container_width=True):
        st.session_state.stage = 'ERA_SELECT'
        st.rerun()

# 2. 시대 선택
elif st.session_state.stage == 'ERA_SELECT':
    st.title("🌀 시간의 틈새")
    st.subheader("정신을 차려보니 시공간이 일그러져 있습니다. 살아남을 시대를 선택하세요!")
    
    era_choice = st.radio("시대를 선택하세요:", list(ERA_DATA.keys()))
    st.info(ERA_DATA[era_choice]["desc"])
    
    if st.button("이 시대로 뛰어들기 🚀", use_container_width=True):
        st.session_state.selected_era = era_choice
        st.session_state.player_dino = random.choice(ERA_DATA[era_choice]["dinos"])
        st.session_state.hp = st.session_state.player_dino["hp"]
        st.session_state.stage = 'FLASH'
        st.rerun()

# 3. 번쩍이는 연출
elif st.session_state.stage == 'FLASH':
    flash_holder = st.empty()
    flash_holder.markdown("<h1 style='text-align: center; font-size: 100px;'>⚡⚡⚡</h1>", unsafe_allow_html=True)
    time.sleep(1)
    st.session_state.stage = 'EGG'
    st.rerun()

# 4. 검은 화면 & 알 부화 연출
elif st.session_state.stage == 'EGG':
    st.title("⬛ 어둠 속에서...")
    st.caption("눈을 떠보니 좁고 컴컴한 공간입니다.")
    
    egg_states = ["🥚", "🥚 (금 가기 시작)", "🥚💥 (금이 쩍쩍 갈라집니다!)", "🐣 부화 성공!"]
    st.markdown(f'<div class="egg-crack">{egg_states[st.session_state.crack_count]}</div>', unsafe_allow_html=True)
    
    if st.session_state.crack_count < 3:
        if st.button("알 껍질 밀어내기! 🔨", use_container_width=True):
            st.session_state.crack_count += 1
            st.rerun()
    else:
        if st.button("밖으로 나가기 ✨", use_container_width=True):
            st.session_state.stage = 'DINO_3D'
            st.rerun()

# 5. 3D 공룡 확인 & 'ㄱㄱ' 버튼
elif st.session_state.stage == 'DINO_3D':
    dino = st.session_state.player_dino
    st.title(f"🦖 당신은 **{dino['name']}**(으)로 태어났습니다!")
    st.write(dino['desc'])
    
    render_3d_dino(dino['name'], dino['color'])
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("ㄱㄱ", use_container_width=True):
            st.session_state.stage = 'PLAYING'
            st.session_state.logs.append(f"[{st.session_state.selected_era}] 시대에 {dino['name']}(으)로 생존을 시작합니다!")
            st.rerun()

# 6. 메인 생존 게임
elif st.session_state.stage == 'PLAYING':
    dino = st.session_state.player_dino
    era = st.session_state.selected_era
    
    st.sidebar.header("📊 현재 상태")
    st.sidebar.write(f"**공룡:** {dino['name']}")
    st.sidebar.write(f"**시대:** {era}")
    st.sidebar.write(f"**생존일:** {st.session_state.day}일 차")
    st.sidebar.progress(max(0, st.session_state.hp) / dino['hp'], text=f"체력: {st.session_state.hp}/{dino['hp']}")
    
    st.title(f"👁️ 1인칭 생존 - {st.session_state.day}일 차")
    st.caption(f"당신({dino['name']})의 눈으로 본 {era}의 세계입니다.")
    
    col1, col2, col3 = st.columns(3)
    action = None
    with col1:
        if st.button("🔍 주변 탐색"): action = "explore"
    with col2:
        if st.button("🍖 먹이 구하기"): action = "eat"
    with col3:
        if st.button("💤 휴식 취하기"): action = "rest"
        
    if action:
        st.session_state.day += 1
        if action == "explore":
            evt = random.choice(ERA_DATA[era]["events"])
            st.session_state.hp -= 15
            st.session_state.logs.append(f"[{st.session_state.day-1}일차] {evt}")
        elif action == "eat":
            st.session_state.hp = min(dino['hp'], st.session_state.hp + 20)
            st.session_state.logs.append(f"[{st.session_state.day-1}일차] 먹이를 먹어 체력을 회복했습니다.")
        elif action == "rest":
            st.session_state.hp = min(dino['hp'], st.session_state.hp + 15)
            st.session_state.logs.append(f"[{st.session_state.day-1}일차] 휴식을 취했습니다.")
            
        if st.session_state.hp <= 0:
            st.error("☠️ 체력이 다하여 생존에 실패했습니다...")
            if st.button("처음부터 다시하기"):
                st.session_state.clear()
                st.rerun()
        else:
            st.rerun()
            
    st.write("---")
    st.subheader("📜 생존 기록")
    for log in reversed(st.session_state.logs):
        st.write(log)
