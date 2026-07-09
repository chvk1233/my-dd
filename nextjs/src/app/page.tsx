import { ZustandDashboard } from "@/widgets/api-fetch-dashboard/ApiFetchDashboard";


// page.tsx : / 주소로 들어왔을때 렌더링 되는 파일
//  -> ZustandDashboard는 데이터의 흐름을 관리하는 컴포넌트가 될거임.
export default function Home() {
  return <ZustandDashboard />;
}