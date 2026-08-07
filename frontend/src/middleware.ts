import { withAuth } from "next-auth/middleware";

export default withAuth({
  pages: { signIn: "/login" },
});

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/jobs/:path*",
    "/candidates/:path*",
    "/rankings/:path*",
    "/comparison/:path*",
    "/interview/:path*",
    "/copilot/:path*",
    "/analytics/:path*",
    "/audit/:path*",
    "/settings/:path*",
    "/tests/:path*",
  ],
};
